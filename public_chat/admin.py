from django.contrib import admin

from .models import PublicChatRoom, PublicChatRoomMessage
from utils.paginator import CachingPaginator


@admin.register(PublicChatRoom)
class PublicChatRoomAdmin(admin.ModelAdmin):
    """Admin for PublicChatRoom model"""
    list_display = ("id", "title")
    list_display_links = ("title",)
    list_filter = ("created_at", "updated_at")
    search_fields = ("title",)


@admin.register(PublicChatRoomMessage)
class PublicChatRoomMessageAdmin(admin.ModelAdmin):
    """Admin for PublicChatRoomMessage model"""
    list_display = ("user", "room", "created_at")
    list_filter = ("created_at", "room")
    search_fields = ("user__username", "room__title", "content")
    readonly_fields = ("user", "room", "content")
    paginator = CachingPaginator
