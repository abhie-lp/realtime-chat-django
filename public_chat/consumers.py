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

        # Add them to group
        await self.channel_layer.group_add(
            "public_chatroom_1",
            self.channel_name
        )

    async def disconnect(self, code):
        """Handle the close request from client websocket"""
        print("PublicChatConsumer", "disconnect")

    async def receive_json(self, content, **kwargs):
        """Handle the data sent from the client websocket"""
        command: str = content.get("command", None)
        message: str = content.get("message", "")

        if command == "send":
            if not message.strip():
                raise RuntimeError("You can't send an empty message.")
            await self.send_message(message)

    async def send_message(self, message):
        user = self.scope["user"]
        await self.channel_layer.group_send(
            "public_chatroom_1",
            {
                "type": "chat.message",     # chat_message
                "profile_image": (user.profile_image.url
                                  if user.profile_image else None),
                "username":  user.username,
                "user_id":  user.id,
                "message":  message,
            }
        )

    async def chat_message(self, event):
        """Handle when there is a message"""

        print("PublicChatConsumer", "chat_message from user", event["user_id"])
        await self.send_json({
            "profile_image": event["profile_image"],
            "username": event["username"],
            "user_id": event["user_id"],
            "message": event["message"],
        })
