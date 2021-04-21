from django.shortcuts import render, get_object_or_404
from django.http.response import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.db import connection

from account.models import Account
from friends.models import FriendRequest, FriendList
from utils.search import binary_search


@login_required()
def my_friend_requests_view(request):
    """View to show all the friend requests of a logged-in user"""
    requests = FriendRequest.objects.select_related("sender").filter(
        receiver=request.user, is_active=True
    ).only("pk", "sender__username", "sender__profile_image")
    ctx = {"friend_requests": requests}
    return render(request, "friends/friend_requests.html", ctx)


@login_required()
def friend_list_view(request, username):
    """View to show all users in friend list"""
    is_self = request.user.username == username
    account = get_object_or_404(Account, username=username) \
        if not is_self else request.user
    friend_list = get_object_or_404(FriendList, user=account)

    # Check if viewing other profile and logged-in user is in their list
    if not is_self and \
            request.user.pk not in \
            friend_list.friends.values_list("pk", flat=True):
        return HttpResponseForbidden("You are not allowed view friend list")

    if is_self:
        # If viewing my own friend list
        # friends = [(account, friendship_status_with_me = True)]
        friends = [
            (friend, True)
            for friend in friend_list.friends.only(
                "pk", "email", "username", "profile_image"
            )
        ]
    else:
        # If viewing other accont's friend list
        my_friends = tuple(FriendList.objects.get(user=request.user).friends
                           .order_by("pk")
                           .values_list("pk", flat=True))
        # friends = [(account, friendship_status_with_me)]
        friends = [
            (user_account, binary_search(user_account.pk, my_friends))
            for user_account in friend_list.friends.only(
                "pk", "username", "email", "profile_image"
            )
        ]
    ctx = {"friends": friends}
    return render(request, "friends/friend_list.html", ctx)
