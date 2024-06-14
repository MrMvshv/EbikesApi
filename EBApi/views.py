from django.http import JsonResponse
from datetime import datetime

def status_ok(request):
    return JsonResponse({'status': 'ok'})

def current_time(request):
    current_time = datetime.now().strftime("%H:%M:%S")
    return JsonResponse({'message': f'Hey, the current time is {current_time}'})
