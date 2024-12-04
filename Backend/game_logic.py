from celery.backends.base import Backend
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import timedelta, datetime
import random
from math import radians, sin, cos, sqrt, atan2
from database_manager import databaseManager
from Backend.hurdles import get_hurdles_for_level

app = Flask(__name__)
CORS(app)

# User Manager Class
class UserManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    # Create a new user or retrieve an existing one
    def get_or_create_user(self, username):

        # Check if th user exists or not
        user = self.db_manager.fetch_one(
            "SELECT id, fuel_consumed FROM User WHERE username = %s", (username)
        )
        if user:
            user_id, fuel_consumed = user
            if fuel_consumed is None:
                fuel_consumed = 500
                self.db_manager.execute_query(
                    "UPDATE User SET fuel_consumed = %s WHERE id = %s", (fuel_consumed, user_id)
                )
            return user_id, fuel_consumed, f"Welcome Back, {username}!!! Resuming from where you left off."
        else:
            # Create a new User
            self.db_manager.execute_query(
                "INSERT INTO User (username, fuel_consumed) VALUES (%s, 500)",(username)
            )
            user_id = self.db_manager.cursor.lastrowid
            return user_id, 500, f"Welcome {username}, thank you for registering!"

# Flight Manager
class FlightManager:
    def __init__(self,db_manager):
        self.db_manager = db_manager

    # Calculate distance in kms using Haversine Formula
    @staticmethod
    def calculate_distance(lat1, lon1, lat2, lon2):
        R = 6371.0
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        distance_lon = lon2 - lon1
        distance_lat = lat2 - lat1
        a = sin(distance_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(distance_lon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c

        return distance

    # Get airports from database
    def get_airports(self,country,continent):
        return self.db_manager.fetch_all(
            """SELECT a.id, a.name, a.latitude_deg, a.longitude_deg 
            FROM Airport a
            JOIN Country c ON a.iso_country = c.iso_country 
            WHERE c.iso_country = %s 
              AND c.continent = %s
            LIMIT 12""",(country,continent)
        )


# Create instances
user_manager = UserManager(db_manager=databaseManager)
flight_manager = FlightManager(db_manager=databaseManager)

# API Routes
@app.route('/user', methods=['POST'])
def create_or_get_user():
    data = request.get_json()
    username = data.get("username")
    if not username:
        return jsonify({"status": "error", "message": "Username is required"}), 400

    user = user_manager.get_or_create_user(username)
    return jsonify({"status": "success", "data": user})

@app.route('/airports', methods=['GET'])
def get_airports():
    country = request.args.get("country")
    continent = request.args.get("continent")

    if not country or not continent:
        return jsonify({"status": "error", "message": "Country and Continent are required"}), 400

    airports = flight_manager.get_airports(country, continent)
    if not airports:
        return jsonify({"status": "error", "message": "No airports found for the given country and continent"}), 404

    return jsonify({"status": "success", "data": airports})

@app.route('/weather', methods=['GET'])
def get_weather():
    level = int(request.args.get("level", 1))
    conditions = ["Sunny", "Windy", "Rainy", "Snowy"]
    weather = {
        "condition": conditions[level - 1],
        "temperature": random.randint(-10, 30),
        "wind_speed": random.randint(5, 40),
        "humidity": random.randint(50, 100),
        "visibility": random.randint(5, 20)
    }
    return jsonify({"status": "success", "data": weather})

@app.route('/flight-duration', methods=['POST'])
def calculate_flight_duration():
    data = request.get_json()
    departure_lat, departure_lon = data.get("departure_lat"), data.get("departure_lon")
    arrival_lat, arrival_lon = data.get("arrival_lat"), data.get("arrival_lon")

    if not all([departure_lat, departure_lon, arrival_lat, arrival_lon]):
        return jsonify({"status": "error", "message": "All coordinates are required"}), 400

    distance = FlightManager.calculate_distance(departure_lat, departure_lon, arrival_lat, arrival_lon)
    speed = 800  # in km/h
    duration_hours = distance / speed
    flight_duration = timedelta(hours=duration_hours)

    return jsonify({"status": "success", "data": {"duration": str(flight_duration), "distance": distance}})

if __name__ == '__main__':
    app.run(debug=True)

