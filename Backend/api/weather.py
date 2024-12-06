import os
from flask import Blueprint, jsonify
from Backend.database_manager import databaseManager
import requests
import logging

weather_bp = Blueprint("weather", __name__)
db = databaseManager()

# Get API key from environment variable
API_KEY = os.getenv('OPENWEATHER_API_KEY')
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

@weather_bp.route("/weather/<string:city>", methods=["GET"])
def get_weather_by_city(city):
    try:
        response = requests.get(
            BASE_URL, 
            params={
                "q": city, 
                "appid": API_KEY, 
                "units": "metric"
            },
            timeout=10  # Add timeout
        )
        response.raise_for_status()  # Raise exception for bad status codes
        data = response.json()

        weather = {
            "city": data["name"],
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"]
        }

        return jsonify({"status": "success", "data": weather}), 200
    except requests.RequestException as e:
        logging.error(f"Weather API error: {str(e)}")
        return jsonify({"status": "error", "message": "Failed to fetch weather data"}), 503
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Fetch dynamic weather data for game simulation
@weather_bp.route("/weather/dynamic", methods=["GET"])
def get_dynamic_weather():
    try:
        query = "SELECT name FROM Airport ORDER BY RAND() LIMIT 1"
        random_airport = db.fetch_one(query)
        if random_airport:
            city = random_airport[0]
            return get_weather_by_city(city)
        return jsonify({"error": "No airport data available"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
