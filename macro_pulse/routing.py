from django.urls import re_path
from indicators.consumers import IndicatorConsumer

websocket_urlpatterns = [
    re_path(r'ws/indicators/$', IndicatorConsumer.as_asgi()),
] 