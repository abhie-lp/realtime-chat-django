from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required()
def private_chat_room_view(request):
    """View for private chat room"""
    ctx = {"debug_mode": settings.DEBUG}
    return render(request, "private_chat/chat_room.html", ctx)
