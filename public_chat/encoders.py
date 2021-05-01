"""Serializer django objects"""

from django.core.serializers.python import Serializer


from .constants import MSG_TYPE_MESSAGE
from .models import PublicChatRoomMessage
from utils.timestamp import humanize_or_normal


class LazyRoomChatMessageEncoder(Serializer):
    """Serializer public chat room chat objects"""
    def get_dump_object(self, obj: PublicChatRoomMessage):
        """Create dict with object details"""
        dump_object = {
            "msg_type": MSG_TYPE_MESSAGE,
            "user_id": obj.user_id,
            "username": obj.user.username,
            "message": obj.content,
            "profile_image": (obj.user.profile_image.url
                              if obj.user.profile_image else None),
            "natural_timestamp": humanize_or_normal(obj.created_at)
        }
        return dump_object
