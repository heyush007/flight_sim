from flask import Blueprint, jsonify
from Backend.database_manager import databaseManager

leaderboard_bp = Blueprint("leaderboard", __name__)
db = databaseManager()

# Fetch top players
@leaderboard_bp.route("/leaderboard/top", methods=["GET"])
def get_top_players():
    query = """
    SELECT u.username, SUM(ufl.flight_time) AS total_time, COUNT(ufl.id) AS flights_completed
    FROM User u
    JOIN User_Flight_Log ufl ON u.id = ufl.user_id
    WHERE ufl.completion_status = 'completed'
    GROUP BY u.id
    ORDER BY total_time DESC
    LIMIT 10
    """
    try:
        result = db.fetch_all(query)
        leaderboard = [
            {
                "username": row[0],
                "total_time": row[1],
                "flights_completed": row[2],
            }
            for row in result
        ]
        return jsonify(leaderboard), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
