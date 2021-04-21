"""URL route for friends app"""

from django.urls import path
from .api import send_friend_request_view, accept_friend_request_view, \
    remove_friend_view, decline_friend_request_view, cancel_friend_request
from .views import my_friend_requests_view, friend_list_view

app_name = "friends"

urlpatterns = [
    path("we-are-friend/<int:pk>/", accept_friend_request_view,
         name="accept_request"),
    path("dont-want-to-be-your-friend/<int:pk>/", decline_friend_request_view,
         name="decline_request"),
    path("i-take-back-my-request/<int:pk>/", cancel_friend_request,
         name="cancel_request"),
    path("we-will-not-talk-anymore", remove_friend_view, name="remove_friend"),
    path("list/<str:username>/", friend_list_view, name="friend_list"),
    path("requests/", my_friend_requests_view, name="friend_requests"),
    path("be-my-friend/", send_friend_request_view, name="send_request"),
]
