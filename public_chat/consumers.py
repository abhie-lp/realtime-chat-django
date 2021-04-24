"""Websocket consumers for public_chat app"""

from datetime import datetime, timedelta

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.humanize.templatetags.humanize import naturalday

from utils.exceptions import ClientError

User = get_user_model()
MSG_TYPE_MESSAGE = 0


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

        try:
            if command == "send":
                if not message.strip():
                    raise ClientError(422, "You can't send an empty message.")
                await self.send_message(message)
        except ClientError as e:
            error_data = {"error": e.code}
            if e.message:
                error_data["message"] = e.message
            await self.send_json(error_data)

    async def send_message(self, message):
        """Send message with data"""
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
            "msg_type": MSG_TYPE_MESSAGE,
            "profile_image": event["profile_image"],
            "username": event["username"],
            "user_id": event["user_id"],
            "message": event["message"],
            "natural_timestamp": chat_timestamp(timezone.now())
        })


def chat_timestamp(timestamp: datetime):
    """
    Format the timestamp of the chat

    1. Today or yesterday:
        - today at 12:45 AM
        - yesterday at 12:30 PM
    2. Other:
        - 24/04/2021
    """
    today = datetime.now()

    if timestamp.date() in (today.date(), (today - timedelta(1)).date()):
        str_time = timestamp.strftime("%I:%M %p").strip("0")
        ts = f"{naturalday(timestamp)} at {str_time}"
    else:
        ts = timestamp.strftime("%d/%m/%Y")
    return ts
