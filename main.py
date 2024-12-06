from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from Backend.api.leaderboard import leaderboard_bp
from Backend.api.achievements import achievements_bp
from Backend.api.progress import progress_bp
from Backend.api.extensions import extensions_bp
from Backend.api.weather import weather_bp
from Backend.api.game_logic import game_bp  # Import the game blueprint

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Register Blueprints with appropriate URL prefixes
app.register_blueprint(game_bp, url_prefix="/api/game")
app.register_blueprint(weather_bp, url_prefix="/api/weather")
app.register_blueprint(leaderboard_bp, url_prefix="/api/leaderboard")
app.register_blueprint(achievements_bp, url_prefix="/api/achievements")
app.register_blueprint(progress_bp, url_prefix="/api/progress")
app.register_blueprint(extensions_bp, url_prefix="/api/extensions")

if __name__ == "__main__":
    app.run(debug=True)
