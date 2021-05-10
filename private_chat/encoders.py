"""Serializer for Django objects"""

from django.core.serializers.python import Serializer
from utils.timestamp import humanize_or_normal

from .constants import MSG_TYPE_MESSAGE
from .models import PrivateRoomChat


class LazyPrivateRoomChatEncoder(Serializer):
    """Serializer for private room chats"""

    def get_dump_object(self, obj: PrivateRoomChat) -> dict:
        """Seriaize the object"""
        return {
            "msg_type": MSG_TYPE_MESSAGE,
            "msg_id": obj.pk,
            "username": obj.user.username,
            "message": obj.content,
            "natural_timestamp": humanize_or_normal(obj.created_at),
            "profile_image": (obj.user.profile_image.url
                              if obj.user.profile_image else None)
        }
