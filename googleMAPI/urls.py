from django.urls import path
from . import views

urlpatterns = [
    path('', views.status, name='status'),
    path('calculate-delivery-fee/', views.calculateDistanceAndDeliveryFeeView.as_view(), name='calculate_distance'),
]