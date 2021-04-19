from django.db import models
from django.conf import settings

from account.models import Account


class FriendList(models.Model):
    """Model to store friends of user"""
    user: Account = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="friend_list"
    )
    friends = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="friends"
    )

    def __str__(self):
        return self.user.username

    def add_friend(self, account):
        """Add friend if not in friend list"""
        if account not in self.friends.all():
            self.friends.add(account)

    def remove_friend(self, account):
        """Remove friend if exists in friend list"""
        if account in self.friends.all():
            self.friends.remove(account)

    def unfriend(self, remover):
        """
        Handle unfriend initiated by remover.
        Remove users from each others friend list.
        """

        # Remove remover from user's friend list
        self.remove_friend(remover)

        # Remove user from remover's friend list
        FriendList.objects.get(user=remover).remove_friend(self.user)

    def is_friend(self, user):
        """Check if user is already friend"""
        return user in self.friends.all()


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
