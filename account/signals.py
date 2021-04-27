"""Signals to execute for the models in account app"""

from django.dispatch.dispatcher import receiver
from django.db.models.signals import post_save

from friends.models import FriendList
from .models import Account


@receiver(post_save, sender=Account)
def create_friend_list_for_new_user(sender, instance, created, **kwargs):
    """Create friendlist for the new user"""
    if created:
        FriendList.objects.create(user=instance)
