"""Routing for websocket"""

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path

from notifications.consumers import NotificationConsumer
from private_chat.consumers import PrivateChatConsumer
from public_chat.consumers import PublicChatConsumer

application = ProtocolTypeRouter({
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter([
                path(
                    "public-chat/<int:room_id>/", PublicChatConsumer.as_asgi()
                ),
                path(
                    "private-chat/<int:room_id>/",
                    PrivateChatConsumer.as_asgi()
                ),
                path("", NotificationConsumer.as_asgi()),
            ])
        )
    )
})
