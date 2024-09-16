from .models import Rider, Location, Order, User
from geopy.geocoders import Nominatim

NAIROBI_CBD_LAT = -1.286389
NAIROBI_CBD_LONG = 36.817223

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
    print('\n', sender_id, '\n')


    # Check if the phone number is in the format +254XXXXXXXXX
    if sender_id.startswith("whatsapp:+254"):
        # Convert to the format 0XXXXXXXXX
        sender_id = "0" + sender_id[13:]

        print(f'\n,Rider Number: {sender_id} \n')
    return Rider.objects.filter(phone_number=sender_id).exists()


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
    print(f'order created : {order}')
    # Return the order ID
    return order.id
    


def get_order_from_db():
    """Get available/pending orders from the database for the riders"""
    return False


def calculate_distance(dropoff, pickup):
    """Calculate distance from pickup to dropoff via GMaps"""
    return False


def delivery_completed():
    """When rider has completed the delivery, change from pending to completed"""
    return False
