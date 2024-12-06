from flask import Blueprint, request, jsonify
from flask_cors import CORS
from datetime import timedelta
import random
from math import radians, sin, cos, sqrt, atan2
from Backend.database_manager import databaseManager
from Backend.hurdles import get_hurdles_for_level
import logging

# Create Blueprint instead of direct Flask app
game_bp = Blueprint("game", __name__)
db_manager = databaseManager()

# For API request tracking
logging.basicConfig(level=logging.INFO)

# Middleware to log requests
@game_bp.before_request
def log_request_info():
    logging.info(f"API Request: {request.method} {request.path}")

# User Manager Class
class UserManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_or_create_user(self, username):
        user = self.db_manager.fetch_one(
            "SELECT id, fuel_consumed FROM User WHERE username = %s", (username,)
        )
        if user:
            user_id, fuel_consumed = user
            if fuel_consumed is None:
                fuel_consumed = 500
                self.db_manager.execute_query(
                    "UPDATE User SET fuel_consumed = %s WHERE id = %s", 
                    (fuel_consumed, user_id)
                )
            return user_id, fuel_consumed, f"Welcome Back, {username}! Resuming from where you left off."
        else:
            self.db_manager.execute_query(
                "INSERT INTO User (username, fuel_consumed) VALUES (%s, %s)",
                (username, 500)
            )
            user_id = self.db_manager.cursor.lastrowid
            return user_id, 500, f"Welcome {username}, thank you for registering!"

# Flight Manager
class FlightManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

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

    def get_airports(self, country, continent):
        return self.db_manager.fetch_all(
            """SELECT a.id, a.name, a.latitude_deg, a.longitude_deg 
            FROM Airport a
            JOIN Country c ON a.iso_country = c.id 
            WHERE c.id = %s 
              AND c.continent = %s
            LIMIT 12""",
            (country, continent)
        )

# Create instances
user_manager = UserManager(db_manager)
flight_manager = FlightManager(db_manager)

# API Routes
@game_bp.route('/user', methods=['POST'])
def create_or_get_user():
    data = request.get_json()
    username = data.get("username")
    if not username:
        return jsonify({"status": "error", "message": "Username is required"}), 400

    user_id, fuel_consumed, message = user_manager.get_or_create_user(username)
    return jsonify({
        "status": "success",
        "data": {
            "user_id": user_id,
            "fuel_consumed": fuel_consumed,
            "message": message
        }
    })

@game_bp.route('/airports', methods=['GET'])
def get_airports():
    country = request.args.get("country")
    continent = request.args.get("continent")

    if not country or not continent:
        return jsonify({"status": "error", "message": "Country and Continent are required"}), 400

    airports = flight_manager.get_airports(country, continent)
    if not airports:
        return jsonify({"status": "error", "message": "No airports found for the given country and continent"}), 404

    return jsonify({"status": "success", "data": airports})

@game_bp.route('/flight-duration', methods=['POST'])
def calculate_flight_duration():
    data = request.get_json()
    departure_lat = data.get("departure_lat")
    departure_lon = data.get("departure_lon")
    arrival_lat = data.get("arrival_lat")
    arrival_lon = data.get("arrival_lon")

    if not all([departure_lat, departure_lon, arrival_lat, arrival_lon]):
        return jsonify({"status": "error", "message": "All coordinates are required"}), 400

    distance = FlightManager.calculate_distance(departure_lat, departure_lon, arrival_lat, arrival_lon)
    speed = 800  # in km/h
    duration_hours = distance / speed
    flight_duration = timedelta(hours=duration_hours)

    return jsonify({
        "status": "success", 
        "data": {
            "duration": str(flight_duration), 
            "distance": distance
        }
    })

@game_bp.route('/flight', methods=['POST'])
def schedule_flight():
    """API to schedule a flight and assign hurdles."""
    try:
        data = request.get_json()
        departure_airport_id = data.get('departure_airport_id')
        arrival_airport_id = data.get('arrival_airport_id')
        scheduled_departure_time = data.get('scheduled_departure_time')
        scheduled_arrival_time = data.get('scheduled_arrival_time')
        level = data.get('level', 1)

        # Generate hurdles for the current level
        hurdles = get_hurdles_for_level(level)

        # Store flight details in the database
        flight_id = db_manager.execute_query(
            """
            INSERT INTO Flight (departure_airport_id, arrival_airport_id, 
                              scheduled_departure_time, scheduled_arrival_time)
            VALUES (%s, %s, %s, %s)
            """,
            (departure_airport_id, arrival_airport_id, 
             scheduled_departure_time, scheduled_arrival_time)
        ).lastrowid

        return jsonify({
            "status": "success",
            "data": {
                "flight_id": flight_id,
                "message": "Flight scheduled successfully",
                "hurdles": hurdles
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

