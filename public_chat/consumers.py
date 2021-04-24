"""Websocket consumers for public_chat app"""

from json import loads, dumps
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth import get_user_model

User = get_user_model()


class PublicChatConsumer(AsyncJsonWebsocketConsumer):
    """Consumer to handle public chat"""

    async def connect(self):
        """Start the connection to client websocket"""
        print("PublicChat connect", self.scope["user"])
        await self.accept()

    async def disconnect(self, code):
        """Handle the close request from client websocket"""
        print("PublicChatConsumer", "disconnect")

    async def receive_json(self, content, **kwargs):
        """Handle the data sent from the client websocket"""
        command = content.get("command", None)
        print("PublicChatConsumer", "receive_json", command)
