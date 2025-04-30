
import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import requests

load_dotenv()

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key')

import os
from pathlib import Path

# Get the absolute path to the data directory
BASE_DIR = Path(__file__).parent.parent  # Goes up one level from src/ to HotelZen/
DATA_DIR = BASE_DIR / 'data'

# Create the data directory if it doesn't exist
DATA_DIR.mkdir(exist_ok=True)

# Define file paths
HOTELS_FILE = DATA_DIR / 'hotels.json'
ROOMS_FILE = DATA_DIR / 'rooms.json'
USERS_FILE = DATA_DIR / 'users.json'
BOOKINGS_FILE = DATA_DIR / 'bookings.json'

# Helper functions to load and save data
def load_data(filepath):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_data(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

# User authentication
def register_user(username, password):
    users = load_data(USERS_FILE)
    if any(user['username'] == username for user in users):
        return False, 'Username already exists'
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = {'id': len(users) + 1, 'username': username, 'password': hashed_password, 'role': 'guest'}
    users.append(new_user)
    save_data(USERS_FILE, users)
    return True, 'User registered successfully'

def authenticate_user(username, password):
    users = load_data(USERS_FILE)
    user = next((user for user in users if user['username'] == username), None)
    if user and bcrypt.check_password_hash(user['password'], password):
        return True, user
    return False, None

# API endpoints
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    success, message = register_user(username, password)
    if success:
        return jsonify({'message': message}), 201
    return jsonify({'message': message}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    success, user = authenticate_user(username, password)
    if success:
        return jsonify({'message': 'Login successful', 'user': {'id': user['id'], 'username': user['username'], 'role': user['role']}}), 200
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/hotels', methods=['GET'])
def get_hotels():
    hotels = load_data(HOTELS_FILE)
    return jsonify(hotels), 200

@app.route('/hotels/<int:hotel_id>', methods=['GET'])
def get_hotel(hotel_id):
    hotels = load_data(HOTELS_FILE)
    hotel = next((hotel for hotel in hotels if hotel['id'] == hotel_id), None)
    if hotel:
        return jsonify(hotel), 200
    return jsonify({'message': 'Hotel not found'}), 404

@app.route('/rooms', methods=['GET'])
def get_rooms():
    rooms = load_data(ROOMS_FILE)
    return jsonify(rooms), 200

@app.route('/rooms/<int:room_id>', methods=['GET'])
def get_room(room_id):
    rooms = load_data(ROOMS_FILE)
    room = next((room for room in rooms if room['id'] == room_id), None)
    if room:
        return jsonify(room), 200
    return jsonify({'message': 'Room not found'}), 404

@app.route('/bookings', methods=['GET', 'POST'])
def manage_bookings():
    if request.method == 'GET':
        bookings = load_data(BOOKINGS_FILE)
        return jsonify(bookings), 200
    elif request.method == 'POST':
        data = request.get_json()
        user_id = data.get('user_id')
        room_id = data.get('room_id')
        check_in_date = data.get('check_in_date')
        check_out_date = data.get('check_out_date')

        bookings = load_data(BOOKINGS_FILE)
        new_booking = {
            'id': len(bookings) + 1,
            'user_id': user_id,
            'room_id': room_id,
            'check_in_date': check_in_date,
            'check_out_date': check_out_date,
            'status': 'confirmed'
        }
        bookings.append(new_booking)
        save_data(BOOKINGS_FILE, bookings)
        return jsonify({'message': 'Booking created successfully', 'booking': new_booking}), 201

@app.route('/bookings/<int:booking_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_booking(booking_id):
    bookings = load_data(BOOKINGS_FILE)
    booking = next((booking for booking in bookings if booking['id'] == booking_id), None)
    if not booking:
        return jsonify({'message': 'Booking not found'}), 404

    if request.method == 'GET':
        return jsonify(booking), 200
    elif request.method == 'PUT':
        data = request.get_json()
        booking['user_id'] = data.get('user_id', booking['user_id'])
        booking['room_id'] = data.get('room_id', booking['room_id'])
        booking['check_in_date'] = data.get('check_in_date', booking['check_in_date'])
        booking['check_out_date'] = data.get('check_out_date', booking['check_out_date'])
        booking['status'] = data.get('status', booking['status'])
        save_data(BOOKINGS_FILE, bookings)
        return jsonify({'message': 'Booking updated successfully', 'booking': booking}), 200
    elif request.method == 'DELETE':
        bookings = [b for b in bookings if b['id'] != booking_id]
        save_data(BOOKINGS_FILE, bookings)
        return jsonify({'message': 'Booking deleted successfully'}), 200

@app.route('/payment', methods=['POST'])
def process_payment():
    data = request.get_json()
    booking_id = data.get('booking_id')
    amount = data.get('amount')

    # Mock payment processing
    if amount > 0:
        return jsonify({'message': 'Payment successful', 'booking_id': booking_id, 'amount': amount}), 200
    else:
        return jsonify({'message': 'Payment failed'}), 400

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('../static', filename)

if __name__ == '__main__':
    app.run(debug=True)
