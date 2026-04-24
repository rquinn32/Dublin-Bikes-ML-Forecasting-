from dotenv import load_dotenv
import os

load_dotenv()

from zoneinfo import ZoneInfo
from datetime import datetime

import requests
from sqlalchemy import create_engine, text


def get_engine():
    user = os.environ["DB_USER"]
    password = os.environ["DB_PASSWORD"]
    host = os.environ.get("DB_HOST", "127.0.0.1")
    port = os.environ.get("DB_PORT", "3306")
    db_name = os.environ["DB_NAME"]

    connection_string = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}"
    return create_engine(connection_string, echo=False)


def fetch_bikes():
    api_key = os.environ["JCDECAUX_API_KEY"]
    contract = os.environ.get("CONTRACT_NAME", "dublin")

    url = "https://api.jcdecaux.com/vls/v1/stations"
    response = requests.get(
        url,
        params={"contract": contract, "apiKey": api_key},
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def to_mysql_datetime(last_update_ms):
    if not last_update_ms:
        return None

    return datetime.fromtimestamp(
        last_update_ms / 1000,
        tz=ZoneInfo("Europe/Dublin")
    ).replace(tzinfo=None)

def insert_bike_snapshots():
    stations = fetch_bikes()
    engine = get_engine()

    insert_sql = text("""
        INSERT IGNORE INTO bike_availability (
            station_id,
            date_time,
            available_bikes,
            available_stands,
            status,
            last_update
        )
        VALUES (
            :station_id,
            :date_time,
            :available_bikes,
            :available_stands,
            :status,
            :last_update
        )
    """)

    inserted = 0

    with engine.begin() as conn:
        for station in stations:
            station_id = station.get("number")
            last_update = station.get("last_update")
            date_time = to_mysql_datetime(last_update)

            if not station_id or not date_time:
                continue

            result = conn.execute(
                insert_sql,
                {
                    "station_id": station_id,
                    "date_time": date_time,
                    "available_bikes": station.get("available_bikes"),
                    "available_stands": station.get("available_bike_stands"),
                    "status": station.get("status"),
                    "last_update": last_update,
                },
            )

            inserted += result.rowcount

    print(f"Bike scraper complete. Inserted {inserted} new rows.")


if __name__ == "__main__":
    insert_bike_snapshots()
