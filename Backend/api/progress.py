from flask import Blueprint, jsonify
from Backend.database_manager import databaseManager

progress_bp = Blueprint("progress", __name__)
db = databaseManager()

# Fetch user progress
@progress_bp.route("/progress/<int:user_id>", methods=["GET"])
def get_user_progress(user_id):
    query = """
    SELECT u.username, COUNT(ufl.id) AS flights_completed, SUM(ufl.flight_time) AS total_time
    FROM User u
    JOIN User_Flight_Log ufl ON u.id = ufl.user_id
    WHERE u.id = %s
    """
    try:
        result = db.fetch_one(query, (user_id,))
        progress = {
            "username": result[0],
            "flights_completed": result[1],
            "total_time": result[2],
        }
        return jsonify(progress), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
