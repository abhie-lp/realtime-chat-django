from django.contrib import admin

from utils.paginator import CachingPaginator
from .models import PrivateRoomChat, PrivateChatRoom


@admin.register(PrivateChatRoom)
class PrivateChatRoomAdmin(admin.ModelAdmin):
    """Admin for PrivateChatRoom model"""
    list_display = ("id", "user1", "user2")
    search_fields = ("user1__username", "user1__email",
                     "user2__username", "user2__email")
    readonly_fields = ("user1", "user2")
    list_filter = "is_active", "created_at"


@admin.register(PrivateRoomChat)
class PrivateRoomChatAdmin(admin.ModelAdmin):
    """Admin for PrivateRoomChat model"""
    list_display = ("id", "user", "room", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "user__email", "content")
    readonly_fields = ("user", "room", "content")
    paginator = CachingPaginator

