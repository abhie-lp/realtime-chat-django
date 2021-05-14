from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin for Notification model"""
    list_display = ("id", "for_user", "by_user", "read", "created_at")
    list_filter = ("read", "created_at", "content_type")
    search_fields = ("for_user__username", "by_user__username")
