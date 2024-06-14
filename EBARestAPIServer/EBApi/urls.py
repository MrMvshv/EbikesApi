from django.urls import path
from . import views

urlpatterns = [
    path('', views.status_ok, name='status-ok'),
    path('time/', views.current_time, name='current-time'),
]
