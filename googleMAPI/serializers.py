from rest_framework import serializers

class DistanceSerializer(serializers.Serializer):
    origin_lat = serializers.FloatField(required=True)
    origin_long = serializers.FloatField(required=True)
    destination_lat = serializers.FloatField(required=True)
    destination_long = serializers.FloatField(required=True)
