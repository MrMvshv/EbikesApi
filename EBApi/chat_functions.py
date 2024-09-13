from .models import Rider

def check_rider(sender_id):
    # checks rider phone number in db

    # Check if the phone number is in the format +254XXXXXXXXX
    if sender_id.startswith("+254"):
        # Convert to the format 0XXXXXXXXX
        sender_id = "0" + sender_id[4:]
    return Rider.objects.filter(phone_number=sender_id).exists()
