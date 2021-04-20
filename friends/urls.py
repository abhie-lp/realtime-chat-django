"""URL route for friends app"""

from django.urls import path
from .api import send_friend_request_view, accept_friend_request_view
from .views import my_friend_requests_view

app_name = "friends"

urlpatterns = [
    path("we-are-friend/<int:pk>/", accept_friend_request_view,
         name="accept_request"),
    path("requests/", my_friend_requests_view, name="friend_requests"),
    path("be-my-friend/", send_friend_request_view, name="send_request"),
]
