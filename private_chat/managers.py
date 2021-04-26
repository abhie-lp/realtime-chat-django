"""Custom managers for private_chat app models"""

from django.db.models import Manager


class RoomChatMessageManager(Manager):
    """Manager to return all chats of a room"""

    def by_room(self, room):
        """Return all the chats in the room"""
        return self.get_queryset().filter(room=room).order_by("-pk")
