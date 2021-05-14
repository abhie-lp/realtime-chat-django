from django.db import models
from django.db.models import Q
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Notification(models.Model):
    """Model for user notification"""

    for_user = models.ForeignKey(settings.AUTH_USER_MODEL,
                                 on_delete=models.CASCADE,
                                 related_name="notification_for")
    by_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,
                                on_delete=models.CASCADE, blank=True,
                                related_name="notification_by")
    redirect_url = models.URLField(max_length=256, null=True, blank=True)
    description = models.CharField(max_length=256, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    def __str__(self):
        return f"{self.by_user.username} -> {self.for_user.username}"
