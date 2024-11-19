from django.db import models
from geopy.distance import geodesic
# models here. -> point to db tables (basically table definitions*)

#store distances for future quick search w/out gMAPI
class DistanceRecord(models.Model):
    origin_lat = models.FloatField()
    origin_long = models.FloatField()
    destination_lat = models.FloatField()
    destination_long = models.FloatField()
    name = models.CharField(max_length=15)
    distance = models.FloatField()
    price = models.FloatField(default=0)

    def __str__(self):
        return f"From ({self.origin_lat}, {self.origin_long}) to ({self.destination_lat}, {self.destination_long} is {self.distance} and {self.price})"

class Rider(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    vehicle_details = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name

class User(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(blank=True, null=True)
    
    def __str__(self):
        return self.name

class Location(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.address
    
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('active', 'Active'),
        ('delivered', 'Delivered'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rider = models.ForeignKey(Rider, on_delete=models.CASCADE, blank=True, null=True)
    pick_up_location = models.ForeignKey(Location, related_name='pick_up_location', on_delete=models.CASCADE)
    drop_off_location = models.ForeignKey(Location, related_name='drop_off_location', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    distance = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order_notes = models.TextField(blank=True, null=True) 
    
    def __str__(self):
        return f"Order {self.id} - {self.status}"

    def save(self, *args, **kwargs):
        if self.pick_up_location and self.drop_off_location:
            pickup_coords = (self.pick_up_location.latitude, self.pick_up_location.longitude)
            dropoff_coords = (self.drop_off_location.latitude, self.drop_off_location.longitude)
            self.distance = round(geodesic(pickup_coords, dropoff_coords).kilometers, 2)
        super().save(*args, **kwargs)


class RiderMemory(models.Model):
    rider_id = models.CharField(max_length=255)  # The sender_id or phone number
    conversation_history = models.TextField()    # Store the conversation as a text (you can store it as JSON too)
    last_updated = models.DateTimeField(auto_now=True)  # To track when the memory was last updated

    def __str__(self):
        return self.rider_id

from django.db import models

class ClientMemory(models.Model):
    client_id = models.CharField(max_length=255)  # The sender_id or phone number
    conversation_history = models.TextField()    # Store the conversation as a text (you can store it as JSON too)
    last_updated = models.DateTimeField(auto_now=True)  # To track when the memory was last updated

    def __str__(self):
        return self.client_id


"""
# quick start table :)


class Table(models.Model):
    col1 = models.Type()
    col2 = models.Type()

    def __str__(self):
        return self.name
Nice :o"""