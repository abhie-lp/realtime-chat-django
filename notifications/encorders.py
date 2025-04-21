"""Serialize notification app models"""

from django.core.serializers.python import Serializer
from django.contrib.humanize.templatetags.humanize import naturaltime

from .models import Notification


class LazyNotificationEncoder(Serializer):
    """Serializer for notifications"""

    def get_dump_object(self, obj: Notification):
        """Serializer the notification object"""
        return {
            "notification_type": obj.model,
            "id": obj.pk,
            "description": obj.description,
            "is_active": (obj.content_type.is_active
                          if obj.model == "friendrequest" else None),
            "is_read": obj.read,
            "natural_timestamp": naturaltime(obj.created_at),
            "timestamp": obj.created_at,
            "redirect_url": obj.redirect_url,
            "image_url": (obj.by_user.profile_url.url
                          if obj.by_user.profile_url else None),
        }
