from rest_framework import serializers

class PlaceSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()

class PayloadSerializer(serializers.Serializer):
    id = serializers.CharField(required=False)
    pickup = serializers.CharField(required=True)
    dropoff = serializers.CharField(required=True)
    return_place = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    customer = serializers.CharField(required=False, default='contact_sxxNtH8')
    meta = serializers.DictField(required=False)
    cod_amount = serializers.IntegerField(required=False, default=0)
    cod_currency = serializers.CharField(required=False, default='KSH')
    cod_payment_method = serializers.CharField(required=False, default='Mpesa')
    type = serializers.CharField(required=True)

class OrderSerializer(serializers.Serializer):
    dispatch = serializers.BooleanField(required=False, default=True)
    type = serializers.CharField(required=False, default='Transport')
    facilitator = serializers.CharField(required=False, default="contact_b995svA")
    customer = serializers.CharField(required=False, default='contact_sxxNtH8')
    notes = serializers.CharField(required=False, allow_blank=True)
    driver = serializers.CharField(required=False, allow_blank=True)
    pickup_name = serializers.CharField(required=True)
    pickup_latitude = serializers.FloatField(required=True)
    pickup_longitude = serializers.FloatField(required=True)
    dropoff_name = serializers.CharField(required=True)
    dropoff_latitude = serializers.FloatField(required=True)
    dropoff_longitude = serializers.FloatField(required=True)
    return_place = serializers.CharField(required=False, allow_blank=True)
    cod_amount = serializers.IntegerField(required=False, default=200)
    cod_currency = serializers.CharField(required=False, allow_blank=True, default='KSH')
    cod_payment_method = serializers.CharField(required=False, allow_blank=True, default='cash')
    order_type = serializers.CharField(required=False, default='Transport')
    delivery_notes = serializers.CharField(required=False, allow_blank=True)