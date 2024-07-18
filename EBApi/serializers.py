from rest_framework import serializers
from .models import DistanceRecord, Rider, User, Location, Order

class DistanceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = DistanceRecord
        fields = '__all__'

class RiderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rider
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

# default serializer :)
'''
class aSerializer(serializers.ModelSerializer):
    class Meta:
        model = a
        fields = '__all__'

'''