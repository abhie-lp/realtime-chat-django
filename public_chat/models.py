from django.conf import settings
from django.db import models

from .managers import PublicChatRoomMessageManager


class PublicChatRoom(models.Model):
    """Model to store public chat room"""
    title = models.CharField(max_length=255, unique=True)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    async def connect_user(self, user):
        """Add user if not in users list and return True else False"""
        if await self.users.filter(pk=user.id).aexists():
            add_status = False
        else:
            await self.users.aadd(user)
            add_status = True
        return add_status

    async def disconnect_user(self, user):
        """Remove user if in users list and return True else False"""
        if await self.users.filter(pk=user.id).aexists():
            await self.users.aremove(user)
            remove_status = True
        else:
            remove_status = False
        return remove_status

    @property
    def group_name(self):
        """Returns the channels group name that sockets should subscribe to"""
        return f"PCR-{self.id}"


class PublicChatRoomMessage(models.Model):
    """Model for chat messages for a public chat room"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    room = models.ForeignKey(PublicChatRoom, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField()

    objects = PublicChatRoomMessageManager()

    def __str__(self):
        return self.content
