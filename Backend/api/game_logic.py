from celery.backends.base import Backend
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import timedelta, datetime
import random
from math import radians, sin, cos, sqrt, atan2
from Backend.database_manager import databaseManager
from Backend.hurdles import get_hurdles_for_level
import logging



app = Flask(__name__)
db_manager = databaseManager()
CORS(app)

# For API request tracking
logging.basicConfig(level=logging.INFO)
logging.info(f"API Request: {request.method} {request.path}")

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
user_manager = UserManager(db_manager)
flight_manager = FlightManager(db_manager)

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
    """Get weather conditions based on level."""
    try:
        level = int(request.args.get("level", 1))  # Default to level 1 if not provided
        hurdles = get_hurdles_for_level(level)  # Generate hurdles based on level

        weather = {
            "condition": hurdles.get("condition", "Sunny"),
            "temperature": hurdles.get("temperature", random.randint(-10, 30)),
            "wind_speed": hurdles.get("wind_speed", random.randint(5, 40)),
            "humidity": hurdles.get("humidity", random.randint(50, 100)),
            "visibility": hurdles.get("visibility", random.randint(5, 20)),
        }
        return jsonify({"status": "success", "data": weather})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


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

@app.route('/user', methods=['POST'])
def handle_user():
    """API to create or fetch a user"""
    data = request.get_json()
    username = data.get('username')

    # Check if the user exists
    user = db_manager.fetch_one("SELECT id, fuel_consumed FROM User WHERE username = %s", (username,))
    if user:
        user_id, fuel_consumed = user
        return jsonify({
            'user_id': user_id,
            'fuel_consumed': fuel_consumed,
            'message': f"Welcome back, {username}!"
        })
    else:
        # Create a new user if doesn't exist
        user_id = db_manager.execute_query(
            "INSERT INTO User (username, fuel_consumed) VALUES (%s, %s)", (username, 500)
        )
        return jsonify({
            'user_id': user_id,
            'fuel_consumed': 500,
            'message': f"Welcome {username}, your profile has been created!"
        })

@app.route('/flight', methods=['POST'])
def schedule_flight():
    """API to schedule a flight and assign hurdles."""
    try:
        data = request.get_json()
        departure_airport_id = data.get('departure_airport_id')
        arrival_airport_id = data.get('arrival_airport_id')
        scheduled_departure_time = data.get('scheduled_departure_time')
        scheduled_arrival_time = data.get('scheduled_arrival_time')
        level = data.get('level', 1)  # Include game level in the flight request

        # Generate hurdles for the current level
        hurdles = get_hurdles_for_level(level)

        # Store flight details in the database
        flight_id = db_manager.execute_query(
            """
            INSERT INTO Flight (departure_airport_id, arrival_airport_id, scheduled_departure_time, scheduled_arrival_time)
            VALUES (%s, %s, %s, %s)
            """,
            (departure_airport_id, arrival_airport_id, scheduled_departure_time, scheduled_arrival_time)
        )

        return jsonify({
            "flight_id": flight_id,
            "message": f"Flight scheduled successfully with hurdles: {hurdles}.",
            "hurdles": hurdles
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/weather', methods=['GET'])
def get_weather():
    """API to get random weather data"""
    weather = db_manager.fetch_all("SELECT * FROM Weather ORDER BY RAND() LIMIT 1")
    return jsonify({
        'weather': weather
    })

if __name__ == '__main__':
    app.run(debug=True)

