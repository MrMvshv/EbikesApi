from django.http import JsonResponse
from datetime import datetime
from rest_framework import generics
from .models import Order, Location, Rider, User
from .serializers import OrderSerializer, LocationSerializer, UserSerializer, RiderSerializer


def status_ok(request):
    return JsonResponse({'status': 'ok'})

def current_time(request):
    current_time = datetime.now().strftime("%H:%M:%S")
    return JsonResponse({'message': f'Hey, the current time is {current_time}'})


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