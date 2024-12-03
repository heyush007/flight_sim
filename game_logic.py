from datetime import timedelta, datetime
import random
import time
import connection
from connect_database import connect_database
from math import radians, sin, cos, sqrt, atan2
from hurdles import get_hurdles_for_level

# Create a new user or retrieve an existing one
def get_or_create_user(cursor, username):
    cursor.execute("SELECT id, fuel_consumed FROM User WHERE username = %s", (username,))
    user = cursor.fetchone()

    if user:
        user_id, fuel_consumed = user
        if fuel_consumed is None:  # If fuel_consumed is NULL, set it to 500
            fuel_consumed = 500
            cursor.execute("UPDATE User SET fuel_consumed = %s WHERE id = %s", (fuel_consumed, user_id))
        print(f"Welcome back, {username}! Resuming from where you left off.")
    else:
        cursor.execute("INSERT INTO User (username, fuel_consumed) VALUES (%s, 500)", (username,))
        user_id = cursor.lastrowid
        fuel_consumed = 500
        print(f"Welcome {username}. Thank you for Registering!")

    return user_id, fuel_consumed

# Fetch available airports based on both the continent and country
def get_airports_for_country_and_continent(cursor, country, continent):
    cursor.execute("""
        SELECT a.id, a.name, a.latitude_deg, a.longitude_deg 
        FROM Airport a
        JOIN Country c ON a.iso_country = c.iso_country 
        WHERE c.iso_country = %s 
          AND c.continent = %s
        LIMIT 12
    """, (country, continent))
    airports = cursor.fetchall()
    return airports

# Insert flight details
def create_flight(cursor, departure_airport_id, arrival_airport_id, departure_time, arrival_time):
    cursor.execute("""
        INSERT INTO Flight (departure_airport_id, arrival_airport_id, scheduled_departure_time, scheduled_arrival_time)
        VALUES (%s, %s, %s, %s)
    """, (departure_airport_id, arrival_airport_id, departure_time, arrival_time))
    return cursor.lastrowid

# Generate random weather conditions
def generate_weather(level):
    conditions = ["Sunny", "Windy", "Rainy", "Snowy"]
    return {
        'condition': conditions[level-1],
        'temperature': random.randint(-10, 30),
        'wind_speed': random.randint(5, 40),
        'humidity': random.randint(50, 100),
        'visibility': random.randint(5, 20)
    }

# Insert weather data
def create_weather(cursor, weather):
    cursor.execute("""
        INSERT INTO Weather (condition, temperature, wind_speed, humidity, visibility)
        VALUES (%s, %s, %s, %s, %s)
    """, (weather['condition'], weather['temperature'], weather['wind_speed'], weather['humidity'], weather['visibility']))
    return cursor.lastrowid

# Calculate distance in kms using Haversine Formula
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    distance_lon = lon2 - lon1
    distance_lat = lat2 - lat1
    a = sin(distance_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(distance_lon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c

    return distance

# Calculate Flight Duration using Haversine Formula
def calculate_flight_duration(departure_airport, arrival_airport):
    departure_lat, departure_lon = departure_airport[2], departure_airport[3]
    arrival_lat, arrival_lon = arrival_airport[2], arrival_airport[3]

    distance = calculate_distance(departure_lat, departure_lon, arrival_lat, arrival_lon)

    speed = 800  # in km/h
    duration_hours = distance / speed

    flight_duration = timedelta(hours=duration_hours)
    return flight_duration, distance

# Game loop
def play_game():
    start_game = input("Do you want to play the game? (yes/no): ").lower()
    if start_game != "yes":
        print("Exiting the game. Have a nice day!")
        return

    connection = connect_database()
    cursor = connection.cursor(buffered=True)

    username = input("Enter your username: ")
    MAX_FUEL_CONSUMED = 500
    user_id, fuel_consumed = get_or_create_user(cursor, username)
    if fuel_consumed is None:
        fuel_consumed = MAX_FUEL_CONSUMED
    print(f"Your current fuel is {fuel_consumed}.")
    update_fuel_in_db(cursor, user_id, fuel_consumed, connection)

    if fuel_consumed < 1:
        print("🚨 ALERT: Fuel Reserves Depleted! 🚨")
        return

    continent = input("Select a continent: ")
    country = input("Select a Country: ") or "FI"

    airports = get_airports_for_country_and_continent(cursor, country, continent)
    if not airports:
        print(f"No airports available for {country} in {continent}.")
        return

    for idx, airport in enumerate(airports):
        print(f"{idx + 1}. {airport[1]} ({airport[2]})")

    departure_index = int(input("Select Departure Airport: ")) - 1
    departure_airport = airports[departure_index]
    arrival_index = int(input("Select Arrival Airport: ")) - 1
    arrival_airport = airports[arrival_index]

    departure_time_str = input("Enter scheduled departure time (YYYY-MM-DD): ")
    scheduled_departure_time = datetime.strptime(departure_time_str, '%Y-%m-%d')

    flight_duration, distance = calculate_flight_duration(departure_airport, arrival_airport)
    scheduled_arrival_time = scheduled_departure_time + flight_duration

    weather = generate_weather(1)
    level = 1
    total_flight_time = timedelta()

    while fuel_consumed > 0:
        print(f"Level {level}")
        print(f"Weather Condition - {weather['condition']}")
        print(f"Your current fuel: {fuel_consumed}")

        for hurdle in get_hurdles_for_level(level):
            print(hurdle['description'])
            user_choice = input("Choose an option (1 or 2): ")

            complexity_percentage = hurdle['complexity'] / 100.0
            if int(user_choice) == hurdle['correct_option']:
                fuel_increase = MAX_FUEL_CONSUMED * complexity_percentage
                fuel_consumed += fuel_increase
                print(f"Fuel increased by {fuel_increase:.2f}. New fuel: {fuel_consumed:.2f}")
            else:
                fuel_loss = MAX_FUEL_CONSUMED * complexity_percentage
                fuel_consumed -= fuel_loss
                print(f"Fuel decreased by {fuel_loss:.2f}. New fuel: {fuel_consumed:.2f}")
                if fuel_consumed <= 0:
                    print("🚨 You ran out of fuel! Game Over 🚨")
                    return
            update_fuel_in_db(cursor, user_id, fuel_consumed, connection)

        total_flight_time += flight_duration
        level += 1
        if level > 4:
            print("Congratulations! You've completed the game.")
            break

        weather = generate_weather(level)

    weather_id = create_weather(cursor, weather)
    flight_id = create_flight(cursor, departure_airport[0], arrival_airport[0], scheduled_departure_time, scheduled_arrival_time)

    cursor.execute("""
        INSERT INTO User_Flight_Log (user_id, flight_id, weather_id, flight_time, completion_status, created_at)
        VALUES (%s, %s, %s, %s, %s, NOW())
    """, (user_id, flight_id, weather_id, total_flight_time, "Completed"))
    connection.commit()
    connection.close()

# Update fuel in database
def update_fuel_in_db(cursor, user_id, fuel_consumed, connection):
    cursor.execute("UPDATE User SET fuel_consumed = %s WHERE id = %s", (fuel_consumed, user_id))
    connection.commit()

if __name__ == "__main__":
    play_game()
