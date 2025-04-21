from .models import Notification
from friends.models import FriendList, FriendRequest
from django.core.paginator import Paginator
from channels.db import database_sync_to_async
from .utils import LazyNotificationEncoder

DEFAULT_NOTIFICATION_PAGE_SIZE = 10


@database_sync_to_async
def general_notifications(user, page_number):
    """Get GENERAL notifications with pagination"""
    notifications = Notification.objects.filter(
        for_user=user,
        content_type__model__in=("friendlist", "friendrequest"),
    ).order_by("-id")
    p = Paginator(notifications, DEFAULT_NOTIFICATION_PAGE_SIZE)
    if notifications.count() > 0 and page_number <= p.num_pages:
        s = LazyNotificationEncoder()
        return {
            "notifications": s.serialize(p.page(page_number).object_list),
            "new_page_number": page_number + 1,
        }
    return None
