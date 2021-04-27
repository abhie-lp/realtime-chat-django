"""Utility functions for private_chat app"""

from django.db.models import Q
from .models import PrivateChatRoom


def get_or_create_chat(user1, user2):
    """Return chat room if exists else create new chat room and return"""
    try:
        return PrivateChatRoom.objects.get(
            Q(user1=user1, user2=user2) |
            Q(user1=user2, user2=user1)
        )
    except PrivateChatRoom.DoesNotExist:
        return PrivateChatRoom.objects.create(user1=user1, user2=user2)
