import requests
import base64
from datetime import datetime
from django.conf import settings

def get_mpesa_access_token():
    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET
    api_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    response = requests.get(api_url, auth=(consumer_key, consumer_secret))

    print(f'Response text: {response.text}')  # Add this line to see the raw response
    print(f'Status code: {response.status_code}')  # Add this line to see the status code
    
    response.raise_for_status()
    return response.json()['access_token']

def lipa_na_mpesa_online(phone_number, amount, account_reference, transaction_desc):
    access_token = get_mpesa_access_token()
    shortcode = settings.MPESA_SHORTCODE
    passkey = settings.MPESA_PASSKEY
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode(shortcode.encode() + passkey.encode() + timestamp.encode()).decode('utf-8')
    amount = ''.join(filter(str.isdigit, amount))

    # Normalize the phone number to the format +254712345678
    phone_number = ''.join(filter(str.isdigit, phone_number))  # Remove non-digit characters
# Normalize the phone number to the format +254712345678
    phone_number = ''.join(filter(str.isdigit, phone_number))  # Remove non-digit characters
    if phone_number.startswith('0'):
        phone_number = '254' + phone_number[1:]
    elif phone_number.startswith('254'):
        phone_number = '254' + phone_number[3:]
    elif phone_number.startswith('254'):
        # Already in the correct format
        pass
    else:
        raise ValueError('Invalid phone number format')    
    print(f"phone:{phone_number}:")
    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": shortcode,
        "PhoneNumber": phone_number,
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": account_reference,
        "TransactionDesc": transaction_desc
    }
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest',
        json=payload,
        headers=headers
    )
    
    return response.json()
