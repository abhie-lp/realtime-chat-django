"""Functions for private_chat app websockets"""

from asgiref.sync import sync_to_async
from django.db.models import Q
from django.core.paginator import Paginator
from channels.db import database_sync_to_async
from django.core.serializers.python import Serializer

from account.encoders import LazyAccountEncoder
from friends.models import FriendList

from utils.exceptions import ClientError

from .constants import DEFAULT_ROOM_CHAT_MESSAGE_PAGE_SIZE
from .models import PrivateChatRoom, PrivateRoomChat
from .encoders import LazyPrivateRoomChatEncoder


async def get_room_or_error(room_id, user) -> PrivateChatRoom:
    """Check and return the private chat room with room_id and user"""
    try:
        room: PrivateChatRoom = await PrivateChatRoom.objects.select_related(
            "user1", "user2"
        ).aget(Q(user1=user) | Q(user2=user), id=room_id)
    except PrivateChatRoom.DoesNotExist:
        raise ClientError("INVALID_ROOM", "Invalid room")
    else:
        # Check if other user in room is currently friend
        other_id = room.user2_id if room.user1_id == user.id else room.user1_id
        if await FriendList.objects.filter(
            user=user, friends__id__in=[other_id]
        ).aexists():
            return room
        else:
            raise ClientError("NOT_A_FRIEND", "You are not a friend")


async def get_user_info(room: PrivateChatRoom, user) -> dict:
    """Function to return serialized user data"""
    other_user = room.user2 if room.user1_id == user.id else room.user1
    serializer = LazyAccountEncoder()
    return (await sync_to_async(serializer.serialize)([other_user]))[0]


async def create_new_private_chat(room, user, message):
    """Create new private chat for the given room and user"""
    return await PrivateRoomChat.objects.acreate(user=user, room=room, content=message)


@database_sync_to_async
def get_private_room_chat_messages(room, page_number) -> dict:
    """Get the chats of the private room"""
    qs = PrivateRoomChat.objects.by_room(room).select_related("user")
    paginator = Paginator(qs, DEFAULT_ROOM_CHAT_MESSAGE_PAGE_SIZE)

    if page_number <= paginator.num_pages:
        serializer: Serializer = LazyPrivateRoomChatEncoder()
        messages = serializer.serialize(paginator.page(page_number).object_list)
        page_number += 1
    else:
        messages = None
    return {"messages": messages, "new_page_number": page_number}
