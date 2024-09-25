import requests
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from datetime import datetime
from rest_framework import generics
from .models import Order, Location, Rider, User
from .serializers import OrderSerializer, LocationSerializer, UserSerializer, RiderSerializer
from .utils import lipa_na_mpesa_online
import json

from .chat import handle_client_conversation, handle_rider_conversation
from .chat_functions import check_rider

def status_ok(request):
    return JsonResponse({'status': 'ok'})

def webhook(request):
    if request.method == 'POST':
        try:
            form_data = request.POST
            # form_data = json.loads(request.body)        # Log the incoming message
            print("Received webhook data")
            print(f'\n\nForm Data: {form_data}\n\n')
            # Extract relevant information (e.g., sender, message content)
            message_text = form_data.get("Body")
            sender_id = form_data.get("From")


            if check_rider(sender_id):
                print(f'found rider, {sender_id}')
                handle_rider_conversation(f"{sender_id}", message_text)      
            else:
                print(f'found user, {sender_id}')
                handle_client_conversation(sender_id, message_text, "normal")

            return JsonResponse({'status': 'success'})
        except Exception as e:
            print(f"Error processing the webhook: {e}")
            return JsonResponse({'status': 'error'})

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

#get order by user or rider
class OrdersByUserView(generics.ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, id=user_id)
        return Order.objects.filter(user=user)

class OrdersByRiderView(generics.ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        rider_id = self.kwargs['rider_id']
        rider = get_object_or_404(Rider, id=rider_id)
        return Order.objects.filter(rider=rider)

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

#query riders by phone number
def find_rider_by_phone(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        phone_number = data.get('phone_number')
        
        if not phone_number:
            return JsonResponse({'status': 'error', 'message': 'Phone number is required'}, status=400)
        
        try:
            rider = Rider.objects.get(phone_number=phone_number)
            return JsonResponse({'status': 'exists', 'rider_id': rider.id})
        except Rider.DoesNotExist:
            return JsonResponse({'status': 'not_found'}, status=404)
    return JsonResponse({'status': 'invalid_method'}, status=405)

# Query user by email
def find_user_by_email(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        
        if not email:
            return JsonResponse({'status': 'error', 'message': 'Email is required'}, status=400)
        
        try:
            user = User.objects.get(email=email)
            return JsonResponse({'status': 'exists', 'user_id': user.id})
        except User.DoesNotExist:
            return JsonResponse({'status': 'not_found'}, status=404)
    return JsonResponse({'status': 'invalid_method'}, status=405)

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

def LocationListSearch(request):
    if request.method == 'POST':
        # Parse the request json data
        data = json.loads(request.body.decode('utf-8'))
        
        # Extract relevant fields from request data
        field_value = data.get('place')  # Replace 'field_name' with the actual field you're filtering by
        
        # Filter the database
        try:
            obj = Location.objects.get(address=field_value)
            return JsonResponse({'status': 'OK', 'id': obj.id})
        except:
            return JsonResponse({'status': 'Not Found'}, status=404)
    return JsonResponse({'status': 'Invalid Request Method'}, status=405)

def AddUser(request):
    if request.method == 'POST':
        try:
            # Parse the incoming JSON data
            data = json.loads(request.body.decode('utf-8'))
            # Log the data (console log)
            print("Received data from Clerk system:", data)
            # Extract the email address from the webhook data
            email_address = data['data']['email_addresses'][0]['email_address']
            print(email_address)
            # Check if the user already exists
            if not User.objects.filter(email=email_address).exists():
                # Create a new user
                user = User.objects.create(
                    name=email_address.split('@')[0],  # use part of the email as the username
                    email=email_address,
                )

                return JsonResponse({'status': 'User created', 'user_id': user.id}, status=201)
            else:
                return JsonResponse({'status': 'User already exists'}, status=200)

        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'status': 'Invalid data'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'Error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'Invalid request method'}, status=405)