"""URL route for friends app"""

from django.urls import path
from .api import send_friend_request_view

app_name = "friends"

urlpatterns = [
    path("be-my-friend/", send_friend_request_view, name="send_request"),
]
