from django.urls import re_path
from websocket.consumers import EconomicDataConsumer

websocket_urlpatterns = [
    re_path(r'ws/economic-data/$', EconomicDataConsumer.as_asgi()),
] 