from .models import Rider, Location, Order, User
from dotenv import load_dotenv
import os
from geopy.geocoders import Nominatim
from django.db.models import Q
import requests

NAIROBI_CBD_LAT = -1.286389
NAIROBI_CBD_LONG = 36.817223

# Load the .env file
load_dotenv()

# Retrieve API key from .env
API_KEY = os.getenv("GOOGLE_API_KEY_DP")

if not API_KEY:
    raise EnvironmentError("API key not found. Please add GMAPS_API_KEY to your .env file.")

def get_client_id(order_id):
    try:
        order = Order.objects.get(id=order_id)
        user_id = order.user.id
        return user_id
    except Order.DoesNotExist:
        return None
    
    
def get_or_create_location(address, latitude, longitude):
    """Get or create a location given the address, latitude, and longitude."""
    location, created = Location.objects.get_or_create(
        address=address,
        defaults={
            'latitude': latitude,
            'longitude': longitude
        }
    )
    return location
    
def get_location_id_by_address(address):
    """Get the location ID by address. Returns the ID if found, else None."""
    try:
        location = Location.objects.get(address=address)
        return location
    except Location.DoesNotExist:
        return None

def update_order_status(order_id, new_status, rider_id):
    """
    Update the status of an order.
    
    Parameters:
        order_id (int): The ID of the order to update.
        new_status (str): The new status to set (must be one of the valid choices).
    
    Returns:
        Order: The updated order object, or None if the order does not exist.
    """
    print(f'\n\nStarting the order, Order Id: {order_id}, with the status {new_status} \n\n')
    try:
        # Retrieve the order by its ID
        order = Order.objects.get(id=order_id)
        # Update the status field if the new status is valid
        if new_status in dict(Order.STATUS_CHOICES):
            print(f'\nOrder Status 2: {order.status} rider {rider_id}\n')
            order.status = new_status
            order.rider = Rider.objects.get(id=rider_id)
            order.save()  # Save the updated order to the database
            return order
        else:
            print(f"Invalid status: {new_status}")
            return None
    except Order.DoesNotExist:
        print(f"Order with ID {order_id} does not exist.")
        return None

def get_lat_long(location_name):
    """Get the latitude and longitude from a location name"""
    
    # Initialize Nominatim API
    geolocator = Nominatim(user_agent="geoapiExercises")
    
    # Get location
    location = geolocator.geocode(location_name)
    
    # If location found, return latitude and longitude
    if location:
        return location.latitude, location.longitude
    else:
        return NAIROBI_CBD_LAT, NAIROBI_CBD_LONG



def check_rider(sender_id):
    # checks rider phone number in db
    print('Checking rider:\n', sender_id, '\n')

    # Check if the phone number is in the format +254XXXXXXXXX
    if sender_id.startswith("whatsapp:+254"):
        # Convert to the format 0XXXXXXXXX
        sender_id = "0" + sender_id[13:]

    return Rider.objects.filter(phone_number=sender_id).exists()


def check_order(order_id):
    try:
        # Retrieve the order by ID
        order = Order.objects.get(id=order_id)
        
        # Check if the order's status is 'active'
        if order.status == 'active' or order.status == 'completed':
            return True
        else:
            return False
    except Order.DoesNotExist:
        # Handle the case where the order does not exist
        print(f'Order with ID {order_id} does not exist.')
        return False

def get_order_id(phone_number):
    #get order where status is active and rider phone number is phone number
    try:
        if phone_number.startswith("whatsapp:+254"):
            phone_number = "0" + phone_number[13:]
            print(f'\nRider Number co: {phone_number} \n')
        # Get the rider with the given phone number
        rider = Rider.objects.get(phone_number=phone_number)

        # Get the active order for the rider
        order = Order.objects.get(rider=rider, status='active')

        # Return the order ID
        return order.id

    except Exception as e:
        # Handle the case where the rider does not exist
        print(f'No rider found with phone number: {phone_number} , error {e}')
        return None

def post_order_from_chat(pickup, dropoff, phone_number, notes, distance):
    """Uploads orders to database from chat"""
     # Get lat/long for pickup and dropoff locations
    # pickup_lat, pickup_long = get_lat_long(pickup)
    # dropoff_lat, dropoff_long = get_lat_long(dropoff)
    # print(pickup_lat, pickup_long, dropoff_lat, dropoff_long)

    phone_number = "0" + phone_number[13:]
    pickup_lat, pickup_long = NAIROBI_CBD_LAT, NAIROBI_CBD_LONG
    dropoff_lat, dropoff_long = NAIROBI_CBD_LAT, NAIROBI_CBD_LONG

     # Create the pickup and dropoff locations
    pickup_location = get_or_create_location(pickup, pickup_lat, pickup_long)
    dropoff_location = get_or_create_location(dropoff, dropoff_lat, dropoff_long)
    print('\n')
    print("p, d:\n", pickup_location, dropoff_location)
    print('\n')
    
    # Find or create the user by phone number
    user, created = User.objects.get_or_create(phone_number=phone_number)
    
    # Create the order
    order = Order.objects.create(
        pick_up_location=pickup_location,
        drop_off_location=dropoff_location,
        user=user,
        order_notes=notes,
        status='Pending'
    )
    print(f'\n\nOrder created : {order}\n\n')
    # Return the order ID
    return order.id
    
def get_rider_by_phone(phone_number):
    # Convert the phone number from "whatsapp:+254" to "0XXXXXXXXX" if needed
    if phone_number.startswith("whatsapp:+254"):
        phone_number = "0" + phone_number[13:]
        print(f'\nRider Number2: {phone_number} \n')

    try:
        # Try to get the rider by phone number
        rider = Rider.objects.get(phone_number=phone_number)
        return rider.id
    except Exception as e:
        # Handle the case where the rider does not exist
        print(f'Rider with phone number {phone_number} does not exist. Error: {e}')
        return 0  # Or handle it in another way as needed

def get_user_by_phone(phone_number):
    #get the rider id or create the rider if does not exist and return id
    if phone_number.startswith("whatsapp:+254"):
        # Convert to the format 0XXXXXXXXX
        phone_number = "0" + phone_number[13:]
        print(f'\n,User Number: {phone_number} \n')
    # Try to get the rider by phone number or create a new one
    user, created = User.objects.get_or_create(phone_number=phone_number)

    if created:
        print(f'New user created with phone number: {phone_number}')
    
    return user.id

def convert_to_whatsapp(phone_number):
    #converts from 07 to whatsapp format (whatsapp:+254)
    if phone_number.startswith('0'):
        formatted_number = 'whatsapp:+254' + phone_number[1:]
    else:
        formatted_number = phone_number
    return formatted_number


def get_order_from_db():
    """Get available/pending orders from the database for the riders"""
    return False

#distance calculators


def get_coordinates(location_name):
    """
    Get latitude and longitude for a given location name using Google Maps Geocoding API.
    
    Args:
        location_name (str): The name of the location.
    
    Returns:
        tuple: (latitude, longitude) of the location.
    """
    geocoding_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": location_name, "key": API_KEY}
    response = requests.get(geocoding_url, params=params)
    data = response.json()
    
    if data["status"] == "OK":
        location = data["results"][0]["geometry"]["location"]
        return location["lat"], location["lng"]
    else:
        raise ValueError(f"Error geocoding {location_name}: {data['status']}")

def get_distance(location1, location2, mode="driving"):
    """
    Calculate the distance between two locations using Google Maps Distance Matrix API.
    
    Args:
        location1 (str): The name of the first location.
        location2 (str): The name of the second location.
        mode (str): Travel mode (e.g., "driving", "walking", "bicycling", "transit").
    
    Returns:
        float: Distance between the two locations in kilometers.
    """
    distance_matrix_url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": location1,
        "destinations": location2,
        "key": API_KEY,
        "mode": mode
    }
    response = requests.get(distance_matrix_url, params=params)
    data = response.json()
    
    if data["status"] == "OK":
        distance_km = data["rows"][0]["elements"][0]["distance"]["value"] / 1000  # meters to km
        return distance_km
    else:
        raise ValueError(f"Error calculating distance: {data['status']}, {data}")


def delivery_completed():
    """When rider has completed the delivery, change from pending to completed"""
    return False