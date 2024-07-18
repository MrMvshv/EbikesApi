from django.urls import path
from . import views

urlpatterns = [
    path('', views.status_ok, name='status-ok'),
    path('time/', views.current_time, name='current-time'),
    path('orders/pending/', views.list_pending_orders, name='list-pending-orders'),
    path('orders/', views.OrderListCreate.as_view(), name='order-list-create'),
    path('orders/<int:pk>/', views.OrderDetail.as_view(), name='order-detail'),
    path('location/', views.LocationListCreate.as_view(), name='location-list-create'),
    path('location/<int:pk>/', views.LocationDetail.as_view(), name='location-detail'),
    path('rider/', views.RiderListCreate.as_view(), name='rider-list-create'),
    path('rider/<int:pk>/', views.RiderDetail.as_view(), name='rider-detail'),
    path('user/', views.UserListCreate.as_view(), name='user-list-create'),
    path('user/<int:pk>/', views.UserDetail.as_view(), name='user-detail'),
]
