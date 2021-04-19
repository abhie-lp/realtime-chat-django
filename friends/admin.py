from django.contrib import admin
from .models import FriendList, FriendRequest


@admin.register(FriendList)
class FriendListAdmin(admin.ModelAdmin):
    """Admin section for FriendList model"""
    list_display = ("user",)
    list_filter = ("user",)
    search_fields = ("user",)
    readonly_fields = ("user",)


@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    """Admin section for FriendRequest model"""
    list_display = ("sender", "receiver", "is_active")
    list_filter = ("is_active",)
    search_fields = ("sender__username", "sender__email",
                     "receiver__username", "receiver__email")
