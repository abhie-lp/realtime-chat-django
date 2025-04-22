from django.core.serializers.python import Serializer
from django.contrib.humanize.templatetags.humanize import naturaltime


class LazyNotificationEncoder(Serializer):
    """Serialize notification into JSON"""

    def get_dump_object(self, obj):
        content_type = obj.model
        dump_object = {
            "notification": content_type,
            "id": obj.id,
            "description": obj.description,
            "read": obj.read,
            "natural_timestamp": str(naturaltime(obj.created_at)),
            "timestamp": obj.created_at.strftime("%Y-%m-%y %H:%M:%S"),
            "actions": {
                    "redirect_url": obj.redirect_url,
            },
            "from": {
                "image_url": img.url if (img := obj.by_user.profile_image) else None
            }
        }
        if content_type == "friendrequest":
            dump_object["active"] = obj.content_object.is_active
            return dump_object
        elif content_type == "friendlist":
            return dump_object
