from datetime import datetime
import numpy as np
import pandas as pd
import pickle
import requests
from flask import current_app

#Load trained long term prediction model
with open("app/models/longterm_model.pkl", "rb") as file:
    model = pickle.load(file)

def fetch_openweather_forecast(target_datetime, city=None):
    """Featch forecasted weather closest to target date/time"""
    api_key = current_app.config.get("OPENWEATHER_API_KEY")
    city = city or current_app.config.get("WEATHER_CITY")

    if not api_key or not city:
        return {}

    url = "https://api.openweathermap.org/data/2.5/forecast"
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
        forecast_list = data.get("list", [])
        if not forecast_list:
            return {}

        # Choose forecast entry closest to the requested date/time
        closest_entry = min(
            forecast_list,
            key=lambda item: abs(datetime.fromtimestamp(item["dt"]) - target_datetime)
        )

        main = closest_entry.get("main", {})
        return {
            "avg_temp": main.get("temp", 0),
            "avg_humidity": main.get("humidity", 0),
            "avg_barometric_pressure": main.get("pressure", 0)
        }

    except Exception:
        return {}

def longterm_prediction(station_id, capacity, city, date_str, time_str):
    """Predict bike availability for a future datetime using long term model"""
    date_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")

    hour = date_time.hour
    day_of_week = date_time.weekday()
    is_weekend = int(day_of_week >= 5)

    #Cyclical encoding of hour
    hour_sin = np.sin(2 * np.pi * hour / 24)
    hour_cos = np.cos(2 * np.pi * hour / 24)

    weather = fetch_openweather_forecast(date_time, city)

    input_data = pd.DataFrame([{
        "station_id": station_id,
        "capacity": capacity,
        "hour_sin": hour_sin,
        "hour_cos": hour_cos,
        "day_of_week": day_of_week,
        "is_weekend": is_weekend,
        "avg_temp": weather.get("avg_temp", 0),
        "avg_humidity": weather.get("avg_humidity", 0),
        "avg_barometric_pressure": weather.get("avg_barometric_pressure", 0)
    }])

    pred = model.predict(input_data)[0]
    prob = model.predict_proba(input_data)[0][1]

    #Return binary prediction + probability score
    return {
        "prediction": int(pred),
        "probability": float(prob)
    }

