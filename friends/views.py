from django.shortcuts import render, get_object_or_404
from django.http.response import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.db import connection

from friends.models import FriendRequest


@login_required()
def my_friend_requests_view(request):
    """View to show all the friend requests of a logged-in user"""
    requests = FriendRequest.objects.filter(
        receiver=request.user, is_active=True
    ).only("sender", "receiver")
    ctx = {"friend_requests": requests}
    return render(request, "friends/friend_requests.html", ctx)
