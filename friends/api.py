"""API views for friend app"""

from django.shortcuts import get_object_or_404
from django.db.models import Q

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_409_CONFLICT, HTTP_403_FORBIDDEN

from account.models import Account
from friends.models import FriendRequest, FriendList


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_friend_request_view(request):
    """View to send friend request to other account."""
    receiver_account = get_object_or_404(
        Account, username=request.data.get("receiver_username")
    )
    try:
        FriendRequest.objects.get(
            Q(sender=request.user, receiver=receiver_account) |
            Q(sender=receiver_account, receiver=request.user),
            is_active=True
        )
    except FriendRequest.DoesNotExist:
        FriendRequest.objects.create(sender=request.user,
                                     receiver=receiver_account)
        return Response("Friend request sent")
    except FriendRequest.MultipleObjectsReturned:
        return Response("You have already sent friend request",
                        status=HTTP_409_CONFLICT)
    else:
        return Response("You have already sent friend request",
                        status=HTTP_409_CONFLICT)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def accept_friend_request_view(request, pk):
    """View to accept a friend request"""
    friend_request = get_object_or_404(FriendRequest, pk=pk)
    if friend_request.receiver != request.user:
        return Response("You don't have permission for this step",
                        status=HTTP_403_FORBIDDEN)
    friend_request.accept()
    return Response("Friend request accepted.")


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def remove_friend_view(request):
    """View to remove a friend from friend list"""
    other_username = request.data.get("username")
    other_account = get_object_or_404(Account, username=other_username)
    FriendList.objects.get(user=request.user).unfriend(other_account)
    return Response("Successfully unfriended")


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def decline_friend_request_view(request, pk):
    """View to decline a friend request"""
    friend_request = get_object_or_404(
        FriendRequest, pk=pk, receiver=request.user
    )
    friend_request.decline()
    return Response("Friend request declined")
