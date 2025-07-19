from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/bidding/$', consumers.BiddingConsumer.as_asgi()),
    re_path(r'ws/team/$', consumers.TeamConsumer.as_asgi()),
] 