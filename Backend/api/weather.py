import requests
from flask import Blueprint, jsonify
from Backend.database_manager import databaseManager

weather_bp = Blueprint("weather", __name__)
db = databaseManager()

API_KEY = "your_openweather_api_key"  # Replace with your API key
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

# Fetch weather data by city name
@weather_bp.route("/weather/<string:city>", methods=["GET"])
def get_weather_by_city(city):
    try:
        response = requests.get(BASE_URL, params={"q": city, "appid": API_KEY, "units": "metric"})
        data = response.json()

        if data.get("cod") != 200:
            return jsonify({"error": data.get("message")}), 404

        weather = {
            "city": data["name"],
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"],
        }

        return jsonify(weather), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
