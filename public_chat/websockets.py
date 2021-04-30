"""Functions related to public_chat app websockets"""

from django.core.paginator import Paginator

from channels.db import database_sync_to_async

from .constants import DEFAULT_PAGE_SIZE
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


@database_sync_to_async
def get_room_chats(room, page_number) -> dict:
    """Get paginated public room chats"""
    qs = (PublicChatRoomMessage.objects
          .by_room(room)
          .select_related("user")
          .only("user__username", "user__profile_image",
                "content", "created_at"))
    pages = Paginator(qs, DEFAULT_PAGE_SIZE)

    new_page_number = page_number
    payload = {}

    # Check if page requested is <= total number of pages
    if new_page_number <= pages.num_pages:
        from .encoders import LazyRoomChatMessageEncoder

        new_page_number = new_page_number + 1
        serializer = LazyRoomChatMessageEncoder()
        payload["messages"] = serializer.serialize(
            pages.page(page_number).object_list
        )
    else:
        payload["messages"] = None
    payload["new_page_number"] = new_page_number
    return payload


@database_sync_to_async
def get_connected_users_count(room: PublicChatRoom) -> int:
    """Return the total number of connected users in room"""
    return room.users.count()

