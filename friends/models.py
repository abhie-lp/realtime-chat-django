from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation

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

    def is_friend(self, user):
        """Check if user is already friend"""
        return user.pk in self.friends.values_list("pk", flat=True)


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

    def decline(self):
        """Decline a friend request from receiver side and update"""
        self.is_active = False
        self.save()

    def cancel(self):
        """Cancel a friend request from sender side and update"""
        self.is_active = False
        self.save()
