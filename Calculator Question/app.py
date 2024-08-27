from flask import Flask, jsonify
import requests

app = Flask(__name__)

# Base URLs for fetching numbers from the external servers
BASE_URL_MAPPING = {
    'e': 'http://20.244.56.144/test/numbers/even',
    'p': 'http://20.244.56.144/test/numbers/primes',
    'f': 'http://20.244.56.144/test/numbers/fibo',
}

# Configuration for the window size
WINDOW_SIZE = 10

# Lists to maintain the current and previous window states
window_curr_state = []
window_prev_state = []

def fetch_numbers(qualified_id):
    """
    Fetch numbers from the external server based on the qualified ID.
    """
    url = BASE_URL_MAPPING.get(qualified_id)
    if not url:
        return []

    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json().get('numbers', [])
        else:
            return []
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return []

@app.route('/numbers/<qualified_id>', methods=['GET'])
def get_average(qualified_id):
    """
    Handle GET requests to calculate the average of numbers fetched from the external server.
    """
    global window_curr_state, window_prev_state

    # Fetch numbers from the external server
    numbers = fetch_numbers(qualified_id)

    # If no numbers were fetched, return the current state with average 0.0
    if not numbers:
        return jsonify({
            "avg": 0.0,
            "numbers": [],
            "windowCurrState": window_curr_state,
            "windowPrevState": window_prev_state
        })

    # Store the previous state before updating the current state
    window_prev_state = window_curr_state.copy()

    # Update the current window state by adding new numbers
    window_curr_state.extend(numbers)

    # Remove duplicates and maintain the size of the window
    window_curr_state = list(set(window_curr_state))
    if len(window_curr_state) > WINDOW_SIZE:
        window_curr_state = window_curr_state[-WINDOW_SIZE:]

    # Calculate the average of the current window state
    avg = sum(window_curr_state) / len(window_curr_state) if window_curr_state else 0.0

    return jsonify({
        "avg": round(avg, 2),
        "numbers": numbers,
        "windowCurrState": window_curr_state,
        "windowPrevState": window_prev_state
    })

if __name__ == '__main__':
    app.run(port=9876)
