from django.core.serializers.python import Serializer
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.urls import reverse


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
            },
        }
        match content_type:
            case "friendrequest":
                dump_object["active"] = obj.content_object.is_active
                request_id = obj.content_object.pk
                dump_object["actions"]["accept"] = reverse(
                    "friends:accept_request", args=(request_id,)
                )
                dump_object["actions"]["deny"] = reverse(
                    "friends:decline_request", args=(request_id,)
                )
                return dump_object
            case "friendlist":
                return dump_object
