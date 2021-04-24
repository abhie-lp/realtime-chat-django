"""Functions related to public_chat app websockets"""

from datetime import datetime, timedelta

from django.contrib.humanize.templatetags.humanize import naturalday

from channels.db import database_sync_to_async

from .models import PublicChatRoom, PublicChatRoomMessage
from utils.exceptions import ClientError


@database_sync_to_async
def connect_user(room: PublicChatRoom, user) -> bool:
    """Add user to the room if not exists"""
    return room.connect_user(user)


@database_sync_to_async
def disconnect_user(room: PublicChatRoom, user) -> bool:
    """Remove user from room if present"""
    return room.disconnect_user(user)


@database_sync_to_async
def get_room_or_error(room_id) -> PublicChatRoom:
    """Get room or raise exception"""
    try:
        return PublicChatRoom.objects.get(pk=room_id)
    except PublicChatRoom.DoesNotExist:
        raise ClientError("ROOM_INVALID", "Room not created")


@database_sync_to_async
def create_new_public_room_chat(room: PublicChatRoom, user, message: str):
    """Add to new chat for the user and room in DB"""
    PublicChatRoomMessage.objects.create(user=user, room=room, content=message)


def chat_timestamp(timestamp: datetime) -> str:
    """
    Format the timestamp of the chat

    1. Today or yesterday:
        - today at 12:45 AM
        - yesterday at 12:30 PM
    2. Other:
        - 24/04/2021
    """
    today = datetime.now()

    # Check if timestamp date ins in today or yesterday
    if timestamp.date() in (today.date(), (today - timedelta(1)).date()):
        str_time = timestamp.strftime("%I:%M %p").strip("0")
        ts = f"{naturalday(timestamp)} at {str_time}"
    else:
        ts = timestamp.strftime("%d/%m/%Y")
    return ts

