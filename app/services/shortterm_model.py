from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import pickle
import requests
from flask import current_app

from app.services.jcdecaux import fetch_live_station_by_id
from app.services.database import get_bikes_nearest_before



#Load trained short term prediction models"""
with open("app/models/lr_10min.pkl", "rb") as file:
    model_10 = pickle.load(file)

with open("app/models/lr_30min.pkl", "rb") as file:
    model_30 = pickle.load(file)

with open("app/models/lr_60min.pkl", "rb") as file:
    model_60 = pickle.load(file)


# Map prediction horizons (minutes) to corresponding models
MODELS = {
    10: model_10,
    30: model_30,
    60: model_60,
}


def fetch_openweather_current(city=None):
    """Fetch current weather features"""
    api_key = current_app.config.get("OPENWEATHER_API_KEY")
    city = city or current_app.config.get("WEATHER_CITY")

    if not api_key or not city:
        return {}

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return {}

        data = response.json()
        main = data.get("main", {})

        return {
            "avg_temp": main.get("temp", 0),
            "avg_humidity": main.get("humidity", 0),
            "avg_barometric_pressure": main.get("pressure", 0)
        }
    except Exception:
        return {}


def get_bikes_now(station_id):
    """Return the current blive bike count for a station"""
    station = fetch_live_station_by_id(station_id)

    if not station:
        return 0

    return int(station.get("available_bikes", 0))


def get_bikes_at_time(station_id, target_dt):
    """Return the nearest recorded bike count at/before given date/time"""
    return get_bikes_nearest_before(station_id, target_dt)


def shortterm_prediction(station_id, capacity, minutes, city=None):
    """ Predict available bikes for a station at 10, 30, 60 min horizons"""
    if minutes not in MODELS:
        raise ValueError("minutes must be one of 10, 30, 60")

    model = MODELS[minutes]
    now = datetime.now()

    hour = now.hour
    day_of_week = now.weekday()
    is_weekend = int(day_of_week >= 5)

    #Cyclical encoding
    hour_sin = np.sin(2 * np.pi * hour / 24)
    hour_cos = np.cos(2 * np.pi * hour / 24)

    weather = fetch_openweather_current(city)
    
    #Use recent historical data as lag features 
    bikes_10mins_ago = get_bikes_at_time(station_id, now - timedelta(minutes=10))
    bikes_30mins_ago = get_bikes_at_time(station_id, now - timedelta(minutes=30))
    bikes_1h_ago = get_bikes_at_time(station_id, now - timedelta(hours=1))
    bikes_24h_ago = get_bikes_at_time(station_id, now - timedelta(hours=24))

    input_data = pd.DataFrame([{
        "station_id": station_id,
        "capacity": capacity,
        "hour_sin": hour_sin,
        "hour_cos": hour_cos,
        "day_of_week": day_of_week,
        "is_weekend": is_weekend,
        "avg_temp": weather.get("avg_temp", 0),
        "avg_humidity": weather.get("avg_humidity", 0),
        "avg_barometric_pressure": weather.get("avg_barometric_pressure", 0),
        "bikes_avail_10mins_ago": bikes_10mins_ago,
        "bikes_avail_30mins_ago": bikes_30mins_ago,
        "bikes_avail_1h_ago": bikes_1h_ago,
        "bikes_avail_24h_ago": bikes_24h_ago
    }])

    pred = model.predict(input_data)[0]
    pred = int(round(float(pred)))
    pred = max(0, min(pred, int(capacity)))

    return pred
