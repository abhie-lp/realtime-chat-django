"""API views for friend app"""

from django.shortcuts import get_object_or_404
from django.db.models import Q

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_409_CONFLICT

from account.models import Account
from friends.models import FriendRequest


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_friend_request_view(request):
    """View to send friend request to other account."""
    print(request.POST.get("receiver_username"))
    receiver_account = get_object_or_404(
        Account, username=request.POST.get("receiver_username")
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


