"""URL mappings for private_chat app"""

from django.urls import path
from .views import private_chat_room_view

app_name = "private_chat"

urlpatterns = [
    path("", private_chat_room_view, name="chat"),
]
