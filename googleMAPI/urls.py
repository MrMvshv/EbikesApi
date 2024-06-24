from django.urls import path
from . import views

urlpatterns = [
    path('', views.status, name='status'),
    path('calculate-distance/', views.calculateDistanceView.as_view(), name='calculate_distance'),
]