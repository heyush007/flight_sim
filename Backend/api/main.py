from flask import Flask
from flask_cors import CORS
from Backend.api.weather import weather_bp
from Backend.api.leaderboard import leaderboard_bp
from Backend.api.achievements import achievements_bp
from Backend.api.progress import progress_bp
from Backend.api.extensions import extensions_bp  # Import the extended API routes

app = Flask(__name__)
CORS(app)

# Register Blueprints
app.register_blueprint(extensions_bp, url_prefix="/api/extensions")
app.register_blueprint(weather_bp, url_prefix="/api/weather")
app.register_blueprint(leaderboard_bp, url_prefix="/api/leaderboard")
app.register_blueprint(achievements_bp, url_prefix="/api/achievements")
app.register_blueprint(progress_bp, url_prefix="/api/progress")


if __name__ == "__main__":
    app.run(debug=True)
