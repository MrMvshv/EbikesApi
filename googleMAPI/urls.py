from django.urls import path
from . import views

urlpatterns = [
    path('', views.status, name='status'),
    path('calculate-distance/', views.calculate_distance, name='calculate_distance'),
]