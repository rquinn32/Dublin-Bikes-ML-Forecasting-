from flask import g, jsonify, current_app
from sqlalchemy import create_engine, text
import os

#Connect to the database and create the engine variable
def connect_to_db():
    """ Create SQLAlchemy engine using app configuration"""
    user = current_app.config["DB_USER"]
    password = current_app.config["DB_PASSWORD"]
    host = current_app.config["DB_HOST"]
    port = current_app.config["DB_PORT"]
    db_name = current_app.config["DB_NAME"]

    connection_string = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}"
    engine = create_engine(connection_string, echo=True)
    return engine

# Create the engine variable and store it in the global Flask variable 'g'
def get_db():
    """ Return a per-request database engine"""
    db_engine = getattr(g, '_database', None)
    if db_engine is None:
        db_engine = g._database = connect_to_db()
    return db_engine

#Show historic station data in json format
def get_stations_from_db():
    engine = get_db()
    stations = []
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT * FROM stations"))
        for row in rows:
            stations.append(dict(row._mapping))
    return stations

#Show historic bike availability data in json
def get_availability_from_db():
    engine = get_db()
    bike_availability = []
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT * FROM bike_availability;"))
        for row in rows:
            bike_availability.append(dict(row._mapping))
    return bike_availability

# Get available bikes data by station ID
def get_availability_by_id_from_db(station_id):
    engine = get_db()
    data = []

    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT * FROM bike_availability WHERE station_id = :id"),
            {"id": station_id}
        )

        for row in rows:
            data.append(dict(row._mapping))

    return data


# Show historic weather data in json
def get_weather_from_db():
    engine = get_db()
    weather = []

    with engine.connect() as conn:
        rows = conn.execute(text("SELECT * FROM weather_hourly;"))

        for row in rows:
            weather.append(dict(row._mapping))

    return weather

# Database reviews
def add_review_to_db(user_email, rating, comments):
    """Insert a new user review into the database"""
    engine = get_db()
    with engine.connect() as conn:
        conn.execute(
            text("""
                INSERT INTO reviews (user_email, rating, comments)
                VALUES (:user_email, :rating, :comments)
            """),
            {
                "user_email": user_email,
                "rating": rating,
                "comments": comments
            }
        )
        conn.commit()


def get_reviews_from_db():
    engine = get_db()
    reviews = []
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT * FROM reviews
            ORDER BY created_at DESC
        """))
        for row in rows:
            reviews.append(dict(row._mapping))
    return reviews



def get_bikes_nearest_before(station_id, target_dt):
    """Return the most recent available_bikes value at or before the given date time. Return 0 if no data exists"""
    engine = get_db()

    with engine.connect() as conn:
        row = conn.execute(
            text("""
                SELECT available_bikes
                FROM bike_availability
                WHERE station_id = :station_id
                  AND date_time <= :target_dt
                ORDER BY date_time DESC
                LIMIT 1
            """),
            {
                "station_id": station_id,
                "target_dt": target_dt
            }
        ).fetchone()

    if row is None:
        return 0

    return int(row._mapping["available_bikes"])
