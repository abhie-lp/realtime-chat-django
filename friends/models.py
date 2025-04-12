from django.db import models
from django.conf import settings
from django.shortcuts import reverse
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType

from account.models import Account
from notifications.models import Notification
from private_chat.utils import get_or_create_chat


class FriendList(models.Model):
    """Model to store friends of user"""
    user: Account = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="friend_list"
    )
    friends = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="friends"
    )

    notifications = GenericRelation(Notification)

    def __str__(self):
        return self.user.username

    def add_friend(self, account):
        """Add friend if not in friend list"""
        self.friends.add(account)

        # Create chat room between two users
        chat = get_or_create_chat(self.user, account)

        # Check if chat is inactive. It means they were friends once.
        # Then stopped being friends and are friends again.
        if not chat.is_active:
            chat.is_active = True
            chat.save()

    def remove_friend(self, account):
        """Remove friend if exists in friend list"""
        self.friends.remove(account)

        # Deactivate the chat room between two friends
        chat = get_or_create_chat(self.user, account)
        if chat.is_active:
            chat.is_active = False
            chat.save()

    def unfriend(self, friend_to_unfriend):
        """
        Handle unfriend initiated by user.
        Remove users from each others friend list.
        """

        # Remove remover from user's friend list
        self.remove_friend(friend_to_unfriend)

        # Remove user from remover's friend list
        friend_to_unfriend.friend_list.remove_friend(self.user)

        # Create notification for the person getting
        self.notifications.create(
            for_user=friend_to_unfriend,
            by_user=self.user,
            redirect_url=reverse("account:view",
                                 args=(friend_to_unfriend.username,)),
            description=f"You are no longer friends with {self.user.username}",
            content_type=ContentType.objects.get_for_model(self)
        )

    async def is_friend(self, user):
        """Check if user is already friend"""
        return await self.friends.filter(pk=user.pk).aexists()


class FriendRequest(models.Model):
    """Model for friend request sent from one user to other"""
    # User sending the request
    sender: Account = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="requests_sent"
    )
    # User receiving the request
    receiver: Account = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="requests_received"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    notifications = GenericRelation(Notification)

    def __str__(self):
        return f"{self.sender.username} --> {self.receiver.username}"

    def accept(self):
        """Accept a  friend request and update sender and receiver"""
        # Add receiver to sender friend-list
        self.sender.friend_list.add_friend(self.receiver)

        # Add sender to receiver friend-list
        self.receiver.friend_list.add_friend(self.sender)

        # Set is_active to False
        self.is_active = False
        self.save()

        # Create a new entry in the Notifications table
        self.notifications.create(
            for_user=self.sender,
            by_user=self.receiver,
            redirect_url=reverse("account:view",
                                 args=(self.receiver.username,)),
            description=f"You are now friends with {self.receiver.username}",
            content_type=ContentType.objects.get_for_model(self),
        )

    def decline(self):
        """Decline a friend request from receiver side and update"""
        self.is_active = False
        self.save()

        self.notifications.create(
            for_user=self.sender,
            by_user=self.receiver,
            redirect_url=reverse("account:view",
                                 args=(self.receiver.username,)),
            description=f"{self.receiver.username} declined you request.",
            content_type=ContentType.objects.get_for_model(self)
        )

    def cancel(self):
        """Cancel a friend request from sender side and update"""
        self.is_active = False
        self.save()
