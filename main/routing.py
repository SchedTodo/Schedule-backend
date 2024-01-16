from django.urls import path
from main.consumer import MyConsumer

websocket_urlpatterns = [
    path('ws/', MyConsumer.as_asgi()),
]
