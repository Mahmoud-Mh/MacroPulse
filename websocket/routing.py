from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/economic_data/$', consumers.EconomicDataConsumer.as_asgi()),
] 