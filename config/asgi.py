"""Routing for websocket"""
import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path
from django.core.asgi import get_asgi_application

from notifications.consumers import NotificationConsumer
from private_chat.consumers import PrivateChatConsumer
from public_chat.consumers import PublicChatConsumer


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
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
