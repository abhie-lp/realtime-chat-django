from django.conf import settings
from django.shortcuts import render


def home_screen_view(request, *args, **kwargs):
    """View for the homescreen"""
    ctx = {
        "debug_mode": settings.DEBUG,
        "room_id": 1
    }
    return render(request, "personal/home.html", ctx)

