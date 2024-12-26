from django.urls import path
from taskifyAPI.consumers import BoardConsumer

websocket_urlpatterns = [
    path('ws/board/<int:board_id>/', BoardConsumer.as_asgi()),
]
