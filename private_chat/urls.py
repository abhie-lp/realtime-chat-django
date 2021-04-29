"""URL mappings for private_chat app"""

from django.urls import path

from .api import get_room_id_with_user_view
from .views import private_chat_room_view

app_name = "private_chat"

urlpatterns = [
    path("meeting-point/", get_room_id_with_user_view, name="private_room_id"),
    path("", private_chat_room_view, name="chat"),
]
