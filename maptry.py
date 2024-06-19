import requests

url = 'https://ebikesbackend-593c3249d102.herokuapp.com/google_api/calculate-distance/'
urls = 'http://127.0.0.1:8000/google_api/calculate-distance/'
data = {"origin_lat": -1.3433182103402546,"origin_long": 36.6600758309724,"destination_lat": -1.3913519108241854,"destination_long": 36.76051708309745}

response = requests.post(urls, data=data)
print(response.json())
