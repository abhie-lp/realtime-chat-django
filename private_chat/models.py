from django.conf import settings
from django.db import models

from .managers import RoomChatMessageManager


class PrivateChatRoom(models.Model):
    """Model for private chat room"""
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE,
                              related_name="user1")
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE,
                              related_name="user2")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user1.username} <---> {self.user2.username}"

    @property
    def group_name(self):
        """Return the group name of the chat"""
        return f"PCR-{self.id}"


class PrivateRoomChat(models.Model):
    """Model to store chat data of user"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    room = models.ForeignKey(PrivateChatRoom, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField()

    objects = RoomChatMessageManager()

    def __str__(self):
        return self.user.username
