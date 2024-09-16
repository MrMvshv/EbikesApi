from django.urls import path
from . import views

urlpatterns = [
    path('', views.status_ok, name='status-ok'),
    path('webhook/', views.webhook, name='webhook'),
    path('time/', views.current_time, name='current-time'),
    path('test-db/', views.test_db_connection, name='test-db'),
    path('orders/pending/', views.list_pending_orders, name='list-pending-orders'),
    path('orders/', views.OrderListCreate.as_view(), name='order-list-create'),
    path('orders/<int:pk>/', views.OrderDetail.as_view(), name='order-detail'),
    path('location/', views.LocationListCreate.as_view(), name='location-list-create'),
    path('location/<int:pk>/', views.LocationDetail.as_view(), name='location-detail'),
    path('rider/', views.RiderListCreate.as_view(), name='rider-list-create'),
    path('rider/<int:pk>/', views.RiderDetail.as_view(), name='rider-detail'),
    path('user/', views.UserListCreate.as_view(), name='user-list-create'),
    path('user/<int:pk>/', views.UserDetail.as_view(), name='user-detail'),

    path('pay/mpesa', views.MpesaPaybill, name='MpesaPaybill'),
    path('res/mpesa', views.MpesaPaybillResponse, name='MpesaPaybillResponse'),

    path('location/search/', views.LocationListSearch, name='location-list-search'),
    path('user/add/', views.AddUser, name='add-user'),

    path('orders/user/<int:user_id>/', views.OrdersByUserView.as_view(), name='orders-by-user-cbv'),
    path('orders/rider/<int:rider_id>/', views.OrdersByRiderView.as_view(), name='orders-by-rider-cbv'),

    path('rider/find-by-phone/', views.find_rider_by_phone, name='find-rider-by-phone'),
    path('user/find-by-email/', views.find_user_by_email, name='find-user-by-email'),
]
