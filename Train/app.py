from flask import Flask, jsonify, request
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

TRAIN_API_URL = "http://20.244.56.144/train/trains"

BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2OTA4MDQ2MzIsImNvbXBhbnlOYW1lIjoiVHJhaW4gQ2VudHJhbCIsImNsaWVudElEIjoiYjM2MTRjZjYtZGEzZC00MzU4LTllNWEtM2I3ODljMWIyYzRlIiwib3duZXJOYW1lIjoiIiwib3duZXJFbWFpbCI6IiIsInJvbGxObyI6IjAyMyJ9.XJngQ-7kkdrNvdhPmFKZ9YORYM04VJwtvP5W0X20PDI"

@app.before_request
def before_request():
    request_headers = dict(request.headers)
    request_headers['Authorization'] = f'Bearer {BEARER_TOKEN}'
    request.headers = request_headers

@app.route('/trains', methods=['GET'])
def get_trains():
    try:
        response = requests.get(TRAIN_API_URL, headers=dict(request.headers))
        response.raise_for_status()

        train_data = response.json()

        if not isinstance(train_data, list):
            raise ValueError("Invalid response data format. Expected a list of trains.")

        current_time = datetime.now()
        def dict_to_str(d):
            return  ":".join(str(y) for y in d.values())
        
        next_12_hours = current_time + timedelta(hours=12)
        filtered_trains = [train for train in train_data if train.get('departureTime') and datetime.strptime(dict_to_str(train['departureTime']), "%H:%M:%S") < next_12_hours]

        for train in filtered_trains:
            train['seatsAvailable'] = {
                'sleeper': train['seatsAvailable']['sleeper'],
                'AC': train['seatsAvailable']['AC']
            }
            train['price'] = {
                'sleeper': train['price']['sleeper'],
                'AC': train['price']['AC']
            }
    #     s =""
    # # print(departure_time_str)
    #     for x,y in departure_time_str.items():
    #         s += str(y)+':'
    #     s = s[:-1]
    # print(s)
        # departure_time = datetime.strptime(s, "%H:%M:%S")

        filtered_trains.sort(key=lambda x: (x['price']['sleeper'], -x['seatsAvailable']['sleeper'], datetime.strptime(dict_to_str(x['departureTime']), "%H:%M:%S")))

        return jsonify(filtered_trains)

    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

#Given challenge with all constraints have been completed the train detail within next 12 hours will be displayed and in ascending order and other users can access this API without bearer token.