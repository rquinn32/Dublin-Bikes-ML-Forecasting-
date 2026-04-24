import os
import requests
from flask import current_app
 

def fetch_bike_api():
    """ Fetch live station data from JCDecaux bikes API"""
    api_key = current_app.config["JCDECAUX_API_KEY"]
    contract = current_app.config["CONTRACT_NAME"]

    url = f"https://api.jcdecaux.com/vls/v1/stations?contract={contract}&apiKey={api_key}"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else []

def fetch_live_station_by_id(station_id):
    """Return a single station from live data by station ID"""
    stations = fetch_bike_api()
    
    # Iterate through live API results to find matching station
    for station in stations:
        if station["number"] == station_id:
            return station
    return None
