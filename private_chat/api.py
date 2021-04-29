"""API views for private_chat app"""

from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from account.models import Account
from .utils import get_or_create_chat


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def get_room_id_with_user_view(request):
    """API to return the room_id between the logged-in user and other user"""
    user1, user2_username = request.user, request.POST.get("user_2")
    user2 = get_object_or_404(Account, username=user2_username)
    response = {"chat_id": get_or_create_chat(user1, user2).pk}
    return Response(response)
