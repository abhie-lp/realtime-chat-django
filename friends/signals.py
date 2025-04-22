"""Signals to execute for friends app"""

from django.shortcuts import reverse
from django.dispatch.dispatcher import receiver
from django.db.models.signals import post_save


from .models import FriendRequest
from notifications.websocket import send_notification


@receiver(post_save, sender=FriendRequest)
def create_friend_request_notification(
    sender, instance: FriendRequest, created, **kwargs
):
    """Create a new notification for the other user"""

    if created:
        notification = instance.notifications.create(
            for_user=instance.receiver,
            by_user=instance.sender,
            redirect_url=reverse("account:view", args=(instance.sender.username,)),
            description=f"{instance.sender.username} sent you a request",
            content_type=instance,
        )
        send_notification(notification, instance.receiver.pk)
