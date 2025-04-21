from django.core.serializers.python import Serializer
from django.contrib.humanize.templatetags.humanize import naturaltime


class LazyNotificationEncoder(Serializer):
    """Serialize notification into JSON"""

    def get_dump_object(self, obj):
        content_type = obj.model
        dump_object = {
            "type": content_type,
            "id": obj.id,
            "description": obj.description,
            "active": obj.content_object.is_active,
            "read": obj.read,
            "natural_timestamp": naturaltime(obj.created_at),
            "timestamp": str(obj.created_at),
            "actions": {
                    "redirect_url": obj.redirect_url,
            },
            "from": {
                "image_url": img.url if (img := obj.by_user.profile_image) else None
            }
        }
        if content_type == "friendrequest":
            return dump_object
        elif content_type == "friendlist":
            return dump_object
