from flask import Blueprint, render_template, jsonify, current_app, request, redirect, url_for, flash
from flask_login import current_user, login_required
from app.services.database import get_reviews_from_db, add_review_to_db
from app.services.user_class import get_user_by_email, create_user
from app.services.longterm_model import longterm_prediction
from app.services.shortterm_model import shortterm_prediction

from app.services.database import (
    get_stations_from_db,
    get_availability_from_db,
    get_availability_by_id_from_db,
    get_weather_from_db
    )

from app.services.jcdecaux import (
    fetch_bike_api,
    fetch_live_station_by_id
    )

from app.services.openweather import (
    fetch_weather_api
    )
    

main_bp = Blueprint("main", __name__)

# Page routes

@main_bp.route("/")
def index():
    """ Render the home page and pass through auth related UI state"""
    reviews = get_reviews_from_db()

    auth = request.args.get("auth")
    token = request.args.get("token")

    return render_template(
        "main/index.html",
        reviews=reviews,
        auth=auth,
        token=token,
        apikey=current_app.config["GOOGLE_MAPS_API_KEY"]
    )

@main_bp.route("/pricing")
def pricing():
    return render_template("pricing/pricing.html")

@main_bp.route("/info")
def info():
    return render_template("info/info.html")

# Review routes

@main_bp.route("/submit_review", methods=["POST"])
@login_required
def submit_review():
    """ Validate and save a user review"""
    rating = request.form.get("rating")
    comments = request.form.get("comments", "").strip()

    if not rating:
        flash("Please select a rating.")
        return redirect(url_for("main.index"))

    try:
        rating = int(rating)
    except ValueError:
        flash("Invalid rating.")
        return redirect(url_for("main.index"))

    if rating < 1 or rating > 5:
        flash("Rating must be between 1 and 5.")
        return redirect(url_for("main.index"))

    add_review_to_db(current_user.email, rating, comments)
    flash("Review submitted successfully.")
    return redirect(url_for("main.index"))

# API routes

@main_bp.route("/api/stations")
def get_stations():
    return jsonify(stations=get_stations_from_db())

@main_bp.route("/api/bike_availability")
def get_availability():
    return jsonify(availability=get_availability_from_db())

@main_bp.route("/api/stations/<int:station_id>")
def get_stations_by_id(station_id):
    return jsonify(available=get_availability_by_id_from_db(station_id))

@main_bp.route("/api/weather_hourly")
def get_weather():
    return jsonify(weather=get_weather_from_db())

# Live data routes

@main_bp.route("/api/live/bikes")
def live_bikes():
    return jsonify(fetch_bike_api())

@main_bp.route("/api/live/bikes/<int:station_id>")
def live_bikes_by_station(station_id):
    station = fetch_live_station_by_id(station_id)
    if station:
        return jsonify(station), 200
    return jsonify({"error": "Station not found"}), 404

@main_bp.route("/api/live/weather")
def weather():
    return jsonify(fetch_weather_api())

# Search route

@main_bp.route("/api/search")
def search_stations():
    """ Return stations whose name or address matches input"""
    query = request.args.get("q", "").strip().lower()
    if not query:
        return jsonify([])

    stations = fetch_bike_api()

    results = [
        station for station in stations
        if query in station.get("name", "").lower()
        or query in station.get("address", "").lower()
    ]

    return jsonify(results)

# Prediction model routes


@main_bp.route("/api/longterm_model")
def longterm_model():
    """ Run the long term prediction model for a station and date/time"""
    date = request.args.get("date")
    time = request.args.get("time")
    station_id = request.args.get("station_id")
    city = request.args.get("city", current_app.config.get("WEATHER_CITY", "Dublin"))

    if not date or not time or not station_id:
        return jsonify({
            "error": "Missing required parameters: date, time, station_id"
        }), 400

    try:
        station_id = int(station_id)

        stations = get_stations_from_db()
        station = next((s for s in stations if int(s["station_id"]) == station_id), None)

        if not station:
            return jsonify({"error": "Station not found"}), 404

        capacity = int(station["bike_stands"])

        result = longterm_prediction(
            station_id=station_id,
            capacity=capacity,
            city=city,
            date_str=date,
            time_str=time
        )

        status = "Bikes Available" if result["prediction"] == 1 else "Likely Empty"

        return jsonify({
            "station_id": station_id,
            "capacity": capacity,
            "city": city,
            "date": date,
             "time": time,
            "status": status,
            "prediction": result["prediction"]
            }), 200

    except ValueError as e:
        return jsonify({"error": f"ValueError: {str(e)}"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500 


@main_bp.route("/api/shortterm_model")
def shortterm_model():
    """Run short term prediction model for a station and horizon"""
    minutes = request.args.get("minutes")
    station_id = request.args.get("station_id")

    if not minutes or not station_id:
        return jsonify({"error": "Missing minutes or station_id"}), 400

    try:
        minutes = int(minutes)
        station_id = int(station_id)

        stations = get_stations_from_db()
        station = next((s for s in stations if int(s["station_id"]) == station_id), None)

        if not station:
            return jsonify({"error": "Station not found"}), 404

        capacity = int(station["bike_stands"])

        result = shortterm_prediction(
            station_id=station_id,
            minutes=minutes,
            capacity=capacity
        )

        return jsonify({
            "station_id": station_id,
            "minutes": minutes,
            "predicted_bikes": result
        }), 200
    

    except Exception as e:
        return jsonify({"error": str(e)}), 500
