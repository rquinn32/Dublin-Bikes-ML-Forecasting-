import requests
from flask import current_app

def fetch_weather_api():
    """ Fetch current weather data from OpenWeather"""
    api_key = current_app.config.get("OPENWEATHER_API_KEY")
    city = current_app.config.get("WEATHER_CITY")

    #Ensure required API config is present
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

        temperature = data.get("main", {}).get("temp")
        wind_speed = data.get("wind", {}).get("speed")
        rain_data = data.get("rain", {})
        rain = rain_data.get("1h", rain_data.get("3h", 0))

        # Return simplified values for frontend use
        return {
            "temperature": round(temperature) if temperature is not None else None,
            "wind_speed": round(wind_speed) if wind_speed is not None else None,
            "rain": round(rain) if rain is not None else 0
        }

    except Exception as e:
        return {}
