from flask import Blueprint, request, jsonify
from Backend.database_manager import databaseManager

extensions_bp = Blueprint("extensions", __name__)
db = databaseManager()

# API to Fetch Checkpoints
@extensions_bp.route("/checkpoints/<int:user_id>", methods=["GET"])
def get_checkpoints(user_id):
    query = """
    SELECT c.id, c.checkpoint_time, c.location_coordinates, c.status
    FROM Checkpoint c
    INNER JOIN User_Flight_Log ufl ON c.user_flight_id = ufl.id
    WHERE ufl.user_id = %s
    """
    try:
        checkpoints = db.fetch_all(query, (user_id,))
        return jsonify(checkpoints), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API to Add a New Hurdle
@extensions_bp.route("/hurdles", methods=["POST"])
def add_hurdle():
    data = request.json
    level = data.get("level")
    description = data.get("description")
    complexity = data.get("complexity")
    correct_option = data.get("correct_option")
    try:
        query = """
        INSERT INTO Hurdles (level, description, complexity, correct_option)
        VALUES (%s, %s, %s, %s)
        """
        db.execute_query(query, (level, description, complexity, correct_option))
        return jsonify({"message": "Hurdle added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API to Manage User Fuel
@extensions_bp.route("/users/<int:user_id>/fuel", methods=["PUT"])
def update_fuel(user_id):
    data = request.json
    fuel_change = data.get("fuel_change", 0)
    try:
        # Update fuel in the database
        query = "UPDATE User SET fuel_consumed = fuel_consumed + %s WHERE id = %s"
        db.execute_query(query, (fuel_change, user_id))
        # Fetch updated fuel
        query = "SELECT fuel_consumed FROM User WHERE id = %s"
        current_fuel = db.fetch_one(query, (user_id,))
        return jsonify({"message": "Fuel updated successfully", "current_fuel": current_fuel[0]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Example for External Data Source Integration
@extensions_bp.route("/external/weather", methods=["GET"])
def get_weather_data():
    # Placeholder for external API integration
    # Implement logic to call weather APIs
    return jsonify({"message": "Weather data fetched successfully"}), 200
