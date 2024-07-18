# EBIKESAPI

REST api server built for Ebikes Africa using django framework.

## API DOCUMENTATION

The API documentation is available on the `/docs` endpoint

<h2> Folder tree Structure </h2>

Ebikes Api

    - EBApi (contains routing configs for EBA ops db)
        - urls.py
        - views.py
        - models.py
        - serializers.py
    - EBARestAPIServer (contains overall server configs and root route switching)
        - asgi.py
        - settings.py
        - urls.py
        - wsgi.py
    - googleMAPI (contains route servr configs for routes using google distance matrix api)
        - urls.py
        - views.py
    - myenv
    - tests
        - maptry.py (test for calculate dist endpoint)
    - manage.py

<h2> Run the app </h2>

After cloning, run

> source myenv/bin/activate

> pip install -r requirements.txt

> python manage.py runserver

- The api should be accessible on localhost:8000

<h2> Routes </h2>

Deployed heroku endpoint: https://ebikesbackend-593c3249d102.herokuapp.com/

- ** not in service **
Paths:

    /       -> root route status, returns 200 ok

    /time   -> returns current server time

    /orders/pending -> returns all pending orders in db as a list

    /{orders | rider | user | location} -> { POST (create) | PUT (update) | DELETE () | GET (retrieve) } the specified item from db

    /{item}/id -> retrieve details of the *item*

<h4> gmapi endpoints </h4>

    /google_api -> returns 200 ok for google maps endpoints accessible

    /google_api/calculate-distance ->

    URL: /google_api/calculate-distance/ Method: POST Permissions: Open to all (AllowAny)

Request Headers Ensure that the request contains the following headers: Content-Type: application/json

# Body Parameters

## Parameter Type Description

    origin_lat float Latitude of the origin
    origin_long float Longitude of the origin
    destination_lat float Latitude of the destination
    destination_long float Longitude of the destination

JSON { "origin_lat": -1.3433182103402546, "origin_long": 6.76600758309724, "destination_lat": -1.3913519108241854, "destination_long": 36.76051708309745}

## Response

Successful Response (200 OK) Returns the delivery price based on the calculated distance. { "delivery_price": 225.0 }
Error Responses

400 Bad Request: Missing required parameters. { "error": "Missing required parameters"}

500 Internal Server Error: Error from the Google API or invalid response structure. { "error": "Error from Google API"}

{ "error": "Invalid response from Google API"}

## How to test with Postman

    Open Postman.
    Create a new request.
    Set the request method to POST.
    Enter the URL: http://127.0.0.1:8000/google_api/calculate-distance/
    Go to the Headers tab and add a new header: Key: Content-Type Value: application/json Go to the Body tab, select raw, and ensure JSON is selected from the dropdown. Enter the request body with the required parameters. (See Example Request Body) Send the request. Check the response in the Postman console. Example Usage Here is an example URL for a local development server:

http://127.0.0.1:8000/google_api/calculate-distance/

For example, to calculate the distance and delivery price between Point A and Point B:

{"origin_lat": -1.3433182103402546,"origin_long": 36.6600758309724,"destination_lat": -1.3913519108241854,"destination_long": 36.76051708309745}
