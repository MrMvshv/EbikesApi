from .models import Rider, Order, Location, RiderMemory, ClientMemory, Location, User  # Replace 'your_app' with the actual app name

def clear_riders():
    """
    Utility function to clear the Rider table.
    """
    Rider.objects.all().delete()
    print("Rider table cleared.")

def clear_users():
    """
    Utility function to clear the Rider table.
    """
    User.objects.all().delete()
    print("User table cleared.")

def clear_orders():
    """
    Utility function to clear the Order table.
    """
    Order.objects.all().delete()
    print("Order table cleared.")

def clear_location():
    """
    Utility function to clear the location table.
    """
    Location.objects.all().delete()
    print("Location table cleared.")

def clear_messages():
    """
    Utility function to clear the location table.
    """
    RiderMemory.objects.all().delete()
    ClientMemory.objects.all().delete()
    print("messages table cleared.")

def clear_all_tables():
    """
    Utility function to clear all relevant tables.
    """
    clear_riders()
    clear_orders()
    clear_location()
    print("All tables cleared.")