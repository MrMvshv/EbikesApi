from django.http import JsonResponse
from datetime import datetime
from rest_framework import generics
from .models import Order, Location, Rider, User
from .serializers import OrderSerializer, LocationSerializer, UserSerializer, RiderSerializer
from .utils import lipa_na_mpesa_online
import json


def status_ok(request):
    return JsonResponse({'status': 'ok'})

def current_time(request):
    current_time = datetime.now().strftime("%H:%M:%S")
    return JsonResponse({'message': f'Hey, the current time is {current_time}'})

def test_db_connection(request):
    try:
        data = list(Order.objects.all().values())
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# class based views for Django to handle CRUD using rest_framework
class OrderListCreate(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class OrderDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class LocationListCreate(generics.ListCreateAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

class LocationDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    
class UserListCreate(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class RiderListCreate(generics.ListCreateAPIView):
    queryset = Rider.objects.all()
    serializer_class = RiderSerializer

class RiderDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Rider.objects.all()
    serializer_class = RiderSerializer


# Mpesa stk push
def MpesaPaybill(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    
    print(data)
    phone_number = data.get('phone_number')
    print(phone_number)
    amount = data.get('amount')
    account_reference = data.get('account_reference')
    transaction_desc = data.get('transaction_desc')
    
    if not phone_number:
        return JsonResponse({'error': 'Phone number is required'}, status=400)
    if not amount:
        return JsonResponse({'error': 'Amount is required'}, status=400)
    if not account_reference:
        return JsonResponse({'error': 'Account reference is required'}, status=400)
    if not transaction_desc:
        return JsonResponse({'error': 'Transaction description is required'}, status=400)
    
    try:
        response = lipa_na_mpesa_online(phone_number, amount, account_reference, transaction_desc)
    except requests.exceptions.RequestException as e:
        # Handle the exception (e.g., log the error, return a custom error message)
        return JsonResponse({'error': str(e)}, status=400)
    
    print(f'response: {response}')
    return JsonResponse(response)

def MpesaPaybillResponse(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    print(data)  # Process the data as needed
    return JsonResponse({'status': 'success response from daraja'})

# methods for retrieving specific data
def list_pending_orders(request):
    # Query all orders with status 'pending'
    pending_orders = Order.objects.filter(status='pending')

    # Serialize the data
    orders_data = [
        {
            'id': order.id,
            'user': order.user.id,
            'rider': order.rider.id if order.rider else None,
            'pick_up_location': order.pick_up_location.id,
            'drop_off_location': order.drop_off_location.id,
            'status': order.status,
            'created_at': order.created_at.isoformat(),
            'updated_at': order.updated_at.isoformat(),
        }
        for order in pending_orders
    ]

    return JsonResponse(orders_data, safe=False)