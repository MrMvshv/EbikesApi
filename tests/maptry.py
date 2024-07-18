import requests

url = 'https://ebikesbackend-593c3249d102.herokuapp.com/google_api/calculate-distance/'
urls = 'http://127.0.0.1:8000/google_api/calculate-distance/'
data = up 

response = requests.post(urls, data=data)
print(response.json())
