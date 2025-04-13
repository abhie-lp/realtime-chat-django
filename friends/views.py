from asgiref.sync import sync_to_async
from django.shortcuts import render
from django.http.response import HttpResponseForbidden
from django.contrib.auth.decorators import login_required

from account.models import Account
from friends.models import FriendRequest, FriendList
from utils.search import binary_search


@login_required()
async def my_friend_requests_view(request):
    """View to show all the friend requests of a logged-in user"""
    request.user = await request.auser()
    qs = FriendRequest.objects.select_related("sender").filter(
        receiver=request.user, is_active=True
    ).only("pk", "sender__username", "sender__profile_image")
    requests = await sync_to_async(tuple)(qs)
    ctx = {"friend_requests": requests}
    return render(request, "friends/friend_requests.html", ctx)


@login_required()
async def friend_list_view(request, username):
    """View to show all users in friend list"""
    request.user = await request.auser()
    own_account = request.user.username == username
    account = await Account.objects.aget(username=username) if not own_account else request.user
    friend_list = await FriendList.objects.select_related("user").aget(user=account)

    # Check if viewing other profile and user is in their list
    if not own_account and not await friend_list.friends.filter(pk=request.user.pk).aexists():
        return HttpResponseForbidden("You are not allowed view friend list")

    if own_account:
        # If viewing my own friend list
        # friends = [(account, friendship_status_with_me = True)]
        friends = [
            (friend, True)
            async for friend in friend_list.friends.only(
                "pk", "email", "username", "profile_image"
            )
        ]
    else: # If viewing other accont's friend list
        # Get logged-in user's friends ids.
        fl = await FriendList.objects.select_related("user").aget(user=request.user)
        my_friends = await sync_to_async(tuple)(fl.friends.order_by("pk").values_list("pk", flat=True))
        # friends = [(account, friendship_status_with_me)]
        friends = [
            (user_account, binary_search(user_account.pk, my_friends))
            async for user_account in friend_list.friends.only(
                "pk", "username", "email", "profile_image"
            )
        ]
    ctx = {"friends": friends}
    return render(request, "friends/friend_list.html", ctx)
