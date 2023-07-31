from flask import Flask, jsonify, request
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

TRAIN_API_URL = "http://20.244.56.144/train/trains"

BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2OTA3OTc1NzcsImNvbXBhbnlOYW1lIjoiVHJhaW4gQ2VudHJhbCIsImNsaWVudElEIjoiYjM2MTRjZjYtZGEzZC00MzU4LTllNWEtM2I3ODljMWIyYzRlIiwib3duZXJOYW1lIjoiIiwib3duZXJFbWFpbCI6IiIsInJvbGxObyI6IjAyMyJ9.3kKFyoShiLXWHFsFpRuL_3OwACnOYrVGjPOTkCqBSRA"

@app.before_request
def before_request():
    request.headers['Authorization'] = f'Bearer {BEARER_TOKEN}'

@app.route('/trains', methods=['GET'])
def get_trains():
    try:
        response = requests.get(TRAIN_API_URL, headers=request.headers)
        response.raise_for_status()

        train_data = response.json()

        current_time = datetime.now()
        filtered_trains = [train for train in train_data if calculate_departure_time(train) > current_time + timedelta(minutes=30)]

        for train in filtered_trains:
            train['seatsAvailable'] = {
                'sleeper': train['seatsAvailable']['sleeper'],
                'AC': train['seatsAvailable']['AC']
            }
            train['price'] = {
                'sleeper': train['price']['sleeper'],
                'AC': train['price']['AC']
            }

        filtered_trains.sort(key=lambda x: (x['price']['sleeper'], -x['seatsAvailable']['sleeper'], calculate_departure_time(x)))

        return jsonify(filtered_trains)

    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

def calculate_departure_time(train):
    departure_time = train['departureTime']
    departure_delay = train['delayedBy']
    departure_datetime = datetime(year=2023, month=7, day=31, hour=departure_time['Hours'], minute=departure_time['Minutes'], second=departure_time['Seconds'])
    return departure_datetime + timedelta(minutes=departure_delay)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
