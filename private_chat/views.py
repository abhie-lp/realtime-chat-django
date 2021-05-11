from django.conf import settings
from django.shortcuts import render
from django.db.models import Q
from django.http.response import HttpResponseNotFound
from django.contrib.auth.decorators import login_required

from private_chat.models import PrivateChatRoom


@login_required()
def private_chat_room_view(request):
    """View for private chat room"""
    user = request.user
    meeting_with = request.GET.get("meeting-with")

    # Check if room exists between two users.
    if meeting_with and not \
            PrivateChatRoom.objects.filter(
                Q(user1=user, user2__username=meeting_with) |
                Q(user1__username=meeting_with, user2=user),
                is_active=True
            ).exists():
        return HttpResponseNotFound(
            f"You are not friends with {meeting_with}. "
            f"Add {meeting_with} as friend to start chat."
        )

    # Get the private chat rooms where user1 = user or user2 = user
    rooms = PrivateChatRoom.objects.select_related("user1", "user2").filter(
        Q(user1=user) | Q(user2=user),
        is_active=True
    ).only(
        "pk", "user1__username", "user1__profile_image",
        "user2__username", "user2__profile_image"
    ).distinct()

    # [{friend: friend-name, message: last-message}, ...]
    frnd_msg = [
        {"friend": (room.user2 if room.user1_id == user.id else room.user1),
         "message": "This is my last message"}
        for room in rooms
    ]
    ctx = {"debug_mode": settings.DEBUG,
           "friend_msg": frnd_msg}

    return render(request, "private_chat/chat_room.html", ctx)
