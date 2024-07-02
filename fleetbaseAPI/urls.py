from django.urls import path
from .views import CreatePlaceView, CreatePayloadView, CreateOrderView, UpdateOrderView
from . import views
urlpatterns = [
    path('', views.status, name='status'),
    path('create-place/', CreatePlaceView.as_view(), name='create-pickup'),
    path('create-payload/', CreatePayloadView.as_view(), name='create-payload'),
    path('create-order/', CreateOrderView.as_view(), name='create-order'),
    path('update-order/', UpdateOrderView.as_view(), name='update-order'),
]
