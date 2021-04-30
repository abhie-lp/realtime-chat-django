"""Functions for private_chat app websockets"""

from django.db.models import Q
from channels.db import database_sync_to_async

from account.encoders import LazyAccountEncoder
from friends.models import FriendList

from .models import PrivateChatRoom


@database_sync_to_async
def get_room_or_error(room_id, user) -> PrivateChatRoom:
    """Check and return the private chat room with room_id and user"""
    try:
        room: PrivateChatRoom = PrivateChatRoom.objects.get(
            Q(user1=user) | Q(user2=user),
            id=room_id
        )
    except PrivateChatRoom.DoesNotExist:
        raise RuntimeError("Invalid room")
    else:
        # Check if other user in room is currently friend
        other_id = room.user2_id if room.user1_id == user.id else room.user1_id
        if FriendList.objects.filter(user=user, friends__id__in=[other_id])\
                .exists():
            return room
        else:
            raise RuntimeError("You are not a friend")


@database_sync_to_async
def get_user_info(room: PrivateChatRoom, user) -> dict:
    """Function to return serialized user data"""
    other_user = room.user2 if room.user1_id == user.id else room.user1
    serializer = LazyAccountEncoder()
    return serializer.serialize([other_user])[0]
