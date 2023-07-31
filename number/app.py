import requests
from flask import Flask, request, jsonify
import time

app = Flask(__name__)

def numberurl(url):
    try:
        response = requests.get(url)  
        if response.status_code == 200:
            data = response.json()
            if "numbers" in data and isinstance(data["numbers"], list):
                return data["numbers"]
    except requests.exceptions.Timeout:
        pass 
    except Exception as e:
        print(f"Error while fetching data from {url}: {e}")
    return []

@app.route("/numbers")
def mergedNumber():
    urls = request.args.getlist("url")
    unique_numbers = set()

    for url in urls:
        numbers = numberurl(url)
        unique_numbers.update(numbers)

    sorted_numbers = sorted(list(unique_numbers))

    return jsonify(numbers=sorted_numbers)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
