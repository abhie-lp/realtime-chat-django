"""Serialize account app models"""

from django.core.serializers.python import Serializer
from .models import Account


class LazyAccountEncoder(Serializer):
    """Serialize the Account model's object"""

    def get_dump_object(self, obj: Account):
        """Perform the serialization"""
        return {
            "id": obj.id,
            "username": obj.username,
            "email": obj.email,
            "profile_image": (obj.profile_image.url
                              if obj.profile_image else None)
        }
