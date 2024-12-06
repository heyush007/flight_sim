from flask import Blueprint, jsonify, request
from Backend.database_manager import databaseManager
import logging

achievements_bp = Blueprint("achievements", __name__)
db = databaseManager()

# Fetch achievements for a user
@achievements_bp.route("/achievements/<int:user_id>", methods=["GET"])
def get_achievements(user_id):
    try:
        query = """
        SELECT achievement_name, achievement_description, status, created_at
        FROM Achievements
        WHERE user_id = %s
        ORDER BY created_at DESC
        """
        achievements = db.fetch_all(query, (user_id,))
        
        if not achievements:
            return jsonify({
                "status": "success",
                "data": [],
                "message": "No achievements found for this user"
            }), 200

        formatted_achievements = [
            {
                "name": ach[0],
                "description": ach[1],
                "status": ach[2],
                "date": ach[3].strftime("%Y-%m-%d %H:%M:%S")
            }
            for ach in achievements
        ]

        return jsonify({
            "status": "success",
            "data": formatted_achievements
        }), 200
    except Exception as e:
        logging.error(f"Error fetching achievements: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Failed to fetch achievements"
        }), 500

# Add a new achievement
@achievements_bp.route("/achievements", methods=["POST"])
def add_achievement():
    data = request.json
    user_id = data.get("user_id")
    name = data.get("achievement_name")
    description = data.get("achievement_description")
    status = data.get("status")

    query = """
    INSERT INTO Achievements (user_id, achievement_name, achievement_description, status)
    VALUES (%s, %s, %s, %s)
    """
    try:
        db.execute_query(query, (user_id, name, description, status))
        return jsonify({"message": "Achievement added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
