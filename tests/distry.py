import requests
import json

# Define the URL
url = "https://bug-free-fishstick-rqw4qvvv5j5f66v-8000.app.github.dev//google_api/calculate-delivery-fee"

# Define the JSON request data
data = {
    "origin_lat": -4.3433182103402546,
    "origin_long": 36.6600758309724,
    "destination_lat": -1.3913519108241854,
    "destination_long": 36.76051708309745
}

try:
    # Send the POST request
    response = requests.post(url, json=data)
    
    # Raise an exception if the request was unsuccessful
    response.raise_for_status()
    
    # Print the response
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())

except requests.exceptions.HTTPError as http_err:
    print(f"HTTP error occurred: {http_err}")
    if response is not None:
        print("Response content:", response.content)
except requests.exceptions.ConnectionError as conn_err:
    print(f"Connection error occurred: {conn_err}")
except requests.exceptions.Timeout as timeout_err:
    print(f"Timeout error occurred: {timeout_err}")
except requests.exceptions.RequestException as req_err:
    print(f"An error occurred: {req_err}")
