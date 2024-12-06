from flask import Blueprint, jsonify
from Backend.database_manager import databaseManager

leaderboard_bp = Blueprint("leaderboard", __name__)
db = databaseManager()

# Fetch top players
@leaderboard_bp.route("/leaderboard", methods=["GET"])
def get_top_players():
    query = """
    SELECT username, total_time, flights_completed
    FROM User
    ORDER BY total_time DESC
    LIMIT 10
    """
    try:
        result = db.fetch_all(query)
        leaderboard = [
            {
                "username": row[0],
                "score": row[1]  # Assuming total_time is the score
            }
            for row in result
        ]
        return jsonify({"status": "success", "data": leaderboard}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
