from .models import Rider, Order, Location  # Replace 'your_app' with the actual app name

def clear_riders():
    """
    Utility function to clear the Rider table.
    """
    Rider.objects.all().delete()
    print("Rider table cleared.")

def clear_orders():
    """
    Utility function to clear the Order table.
    """
    Order.objects.all().delete()
    print("Order table cleared.")

def clear_all_tables():
    """
    Utility function to clear all relevant tables.
    """
    clear_riders()
    clear_orders()
    print("All tables cleared.")

def clear_location():
    """
    Utility function to clear the location table.
    """
    Location.objects.all().delete()
    print("Location table cleared.")
