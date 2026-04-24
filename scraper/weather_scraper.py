from dotenv import load_dotenv
import os

load_dotenv()
from datetime import datetime

import requests
from sqlalchemy import create_engine, text
from zoneinfo import ZoneInfo

def get_engine():
    user = os.environ["DB_USER"]
    password = os.environ["DB_PASSWORD"]
    host = os.environ.get("DB_HOST", "127.0.0.1")
    port = os.environ.get("DB_PORT", "3306")
    db_name = os.environ["DB_NAME"]

    connection_string = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}"
    return create_engine(connection_string, echo=False)


def fetch_weather():
    api_key = os.environ["OPENWEATHER_API_KEY"]
    city = os.environ.get("WEATHER_CITY", "Dublin")

    url = "https://api.openweathermap.org/data/2.5/weather"
    response = requests.get(
    url,
    params={
        "lat": 53.3498,
        "lon": -6.2603,
        "appid": api_key,
        "units": "metric"
    },
    timeout=20
    )
    response.raise_for_status()
    return response.json()


def insert_weather_snapshot():
    data = fetch_weather()
    engine = get_engine()

    dt_unix = data.get("dt")
    if not dt_unix:
        raise ValueError("Weather response missing 'dt' timestamp")

    date_time = datetime.fromtimestamp(
    dt_unix,
    tz=ZoneInfo("Europe/Dublin")
    ).replace(tzinfo=None)

    main = data.get("main", {})
    wind = data.get("wind", {})
    rain = data.get("rain", {})
    snow = data.get("snow", {})
    weather_list = data.get("weather", [])
    weather = weather_list[0] if weather_list else {}

    insert_sql = text("""
        INSERT IGNORE INTO weather_hourly (
            date_time,
            temp,
            feels_like,
            humidity,
            pressure,
            wind_speed,
            wind_gust,
            rain_1h,
            snow_1h,
            weather_id,
            weather_main,
            weather_desc
        )
        VALUES (
            :date_time,
            :temp,
            :feels_like,
            :humidity,
            :pressure,
            :wind_speed,
            :wind_gust,
            :rain_1h,
            :snow_1h,
            :weather_id,
            :weather_main,
            :weather_desc
        )
    """)

    with engine.begin() as conn:
        result = conn.execute(
            insert_sql,
            {
                "date_time": date_time,
                "temp": main.get("temp"),
                "feels_like": main.get("feels_like"),
                "humidity": main.get("humidity"),
                "pressure": main.get("pressure"),
                "wind_speed": wind.get("speed"),
                "wind_gust": wind.get("gust"),
                "rain_1h": rain.get("1h"),
                "snow_1h": snow.get("1h"),
                "weather_id": weather.get("id"),
                "weather_main": weather.get("main"),
                "weather_desc": weather.get("description"),
            },
        )

    print(f"Weather scraper complete. Inserted {result.rowcount} new row(s).")


if __name__ == "__main__":
    insert_weather_snapshot()
