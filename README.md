# Overview
This is a terminal-based flight simulator game where players can choose airports, fly between them, and face various weather-based challenges. The goal is to navigate successfully through different weather conditions while making strategic decisions to keep the flight on course.

## Setup the Game
Clone the repository.
- Ensure you have the necessary Python packages installed. : Python 3.12
- Set up the MariaDB database on your device.
- Create a new database locally.

## Setup Database
- After creating the database, change the host, port, database, user and password as set. 
- Run Setup_database > setup_db.py file.

## How to Play
### Start the Game:
Launch the game by running the main.py file in your terminal or, simply type in terminal:
```
python main.py
```
### Enter Username:
- Input your username to start. 
- If you are a returning player, the game will load your last checkpoint.

Select Flight Details:

- Choose a continent.
- Select a country.
- Choose a departure and arrival airport.
- Weather Challenges:
  - As you fly, you will face weather-related hurdles such as turbulence, rainstorms, and wind conditions. Make decisions based on the provided options to keep your flight stable.

Flight Progress:
- The game will track your progress, calculate flight time, and adjust weather conditions as you fly.

Save and Resume:
- The game automatically saves your progress at checkpoints. You can resume from the last saved point if you exit the game.

### Basic Controls
- Use 1 or 2 to select options during weather challenges.
- Follow on-screen instructions for navigation and decision-making.

