from .models import Rider, Location, Order, User
from geopy.geocoders import Nominatim
from django.db.models import Q

NAIROBI_CBD_LAT = -1.286389
NAIROBI_CBD_LONG = 36.817223

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
        if order.status == 'active':
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

def post_order_from_chat(pickup, dropoff, phone_number, notes):
    """Uploads orders to database from chat"""
     # Get lat/long for pickup and dropoff locations
    # pickup_lat, pickup_long = get_lat_long(pickup)
    # dropoff_lat, dropoff_long = get_lat_long(dropoff)
    # print(pickup_lat, pickup_long, dropoff_lat, dropoff_long)

    phone_number = "0" + phone_number[13:]
    pickup_lat, pickup_long = NAIROBI_CBD_LAT, NAIROBI_CBD_LONG
    dropoff_lat, dropoff_long = NAIROBI_CBD_LAT, NAIROBI_CBD_LONG

     # Create the pickup and dropoff locations
    pickup_location = Location.objects.create(
        address=pickup, 
        latitude=pickup_lat, 
        longitude=pickup_long
    )
    dropoff_location = Location.objects.create(
        address=dropoff, 
        latitude=dropoff_lat, 
        longitude=dropoff_long
    )
    print('\n')
    print(pickup_location, dropoff_location)
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

def get_order_from_db():
    """Get available/pending orders from the database for the riders"""
    return False


def calculate_distance(dropoff, pickup):
    """Calculate distance from pickup to dropoff via GMaps"""
    return False


def delivery_completed():
    """When rider has completed the delivery, change from pending to completed"""
    return False
