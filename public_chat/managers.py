"""Custom Managers for models"""

from django.db.models import Manager


class PublicChatRoomMessageManager(Manager):
    """Manager for PublicChatRoomMessage model"""

    def by_room(self, room):
        """Return all the messages of a room"""
        return self.get_queryset().filter(room=room).order_by("-pk")
