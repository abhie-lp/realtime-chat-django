"""Websocket consumers for private_chat app"""

from django.utils import timezone
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from utils.exceptions import ClientError
from utils.timestamp import humanize_or_normal

from .constants import *
from .websockets import get_user_info, get_room_or_error, \
    create_new_private_chat


class PrivateChatConsumer(AsyncJsonWebsocketConsumer):
    """Chat consumer"""

    async def connect(self):
        """Initiating the handshake."""
        print("PrivateChatConsumer", "connect", self.scope["user"])

        await self.accept()

        # room_id acts as a check if connected or else None.
        self.room = None

    async def receive_json(self, content, **kwargs):
        """
        Called when receiving a message.
        Check the content to process further
        """

        command = content.get("command", None)
        room_id = content.get("room_id")
        logged_user = self.scope["user"]
        print("PrivateChatConsumer", "receive_json", command, room_id)

        try:
            if command == "JOIN":
                await self.join_room(room_id)
            elif command == "LEAVE":
                await self.leave_room(room_id)
            elif command == "SEND":
                if len(content["message"].lstrip()) != 0:
                    await self.send_room(room_id, content["message"])
            elif command == "ROOM_CHATS":
                pass
            elif command == "USER_INFO":
                room = await get_room_or_error(room_id, logged_user)
                user_info = await get_user_info(room, logged_user)
                await self.send_user_info(user_info)
        except ClientError as e:
            await self.handle_client_error(e)

    async def disconnect(self, code):
        """Called when websocket closes"""
        print("PrivateChatConsumer", "disconnect")
        if self.room is not None:
            await self.leave_room(self.room.id)

    async def join_room(self, room_id):
        """Called when JOIN command is received in receive_json"""
        print("PrivateChatConsumer", "join_room", room_id)
        self.room = await get_room_or_error(room_id, self.scope["user"])

        # Add to the group
        await self.channel_layer.group_add(
            self.room.group_name,
            self.channel_name
        )

        await self.send_json({
            "join": room_id
        })

        if self.scope["user"].is_authenticated:
            user = self.scope["user"]
            await self.channel_layer.group_send(
                self.room.group_name,
                {
                    "type": "chat.join",
                    "room_id": self.room.id,
                    "username": user.username,
                    "profile_image": (user.profile_image.url
                                      if user.profile_image else None)
                }
            )

    async def leave_room(self, room_id):
        """Called when LEAVE command is received in receive_json"""
        print("PrivateChatConsumer", "leave_room", room_id)

        user = self.scope["user"]

        await self.channel_layer.group_send(
            self.room.group_name,
            {
                "type": "chat.leave",
                "room_id": self.room.id,
                "username": user.username,
                "profile_image": (user.profile_image.url
                                  if user.profile_image else None)
            }
        )

        await self.channel_layer.group_discard(
            self.room.group_name,
            self.channel_name
        )

        self.room = None

        await self.send_json({
            "leave": room_id
        })

    async def send_room(self, room_id, message):
        """Called in receive_json to send a message to private room"""
        print("PrivateChatConsumer", "send_json", room_id)
        if self.room is not None and self.room.id == room_id:
            user = self.scope["user"]

            # Store the message in DB
            await create_new_private_chat(self.room, user, message)

            # Transfer the message to client and other user
            await self.channel_layer.group_send(
                self.room.group_name,
                {
                    "type": "chat.message",
                    "username": user.username,
                    "user_id": user.id,
                    "profile_image": (user.profile_image.url
                                      if user.profile_image else None),
                    "message": message
                }
            )
        else:
            raise ClientError("ROOM_ACCESS_DENIED", "Room access denied")

    async def chat_join(self, event):
        """Called when someone has joined the chat"""
        print("PrivateChatConsumer", "chat_join", self.scope["user"])
        if event["username"]:
            await self.send_json({
                "msg_type": MSG_TYPE_ENTER,
                "room_id": event["room_id"],
                "profile_image": event["profile_image"],
                "username": event["username"],
                "message": event["username"] + " connected."
            })

    async def chat_leave(self, event):
        """Called when someone leaves the chat"""
        print("PrivateChatConsumer", "chat_leave")
        if event["username"]:
            await self.send_json({
                "msg_type": MSG_TYPE_LEAVE,
                "room_id": event["room_id"],
                "profile_image": event["profile_image"],
                "username": event["username"],
                "message": event["username"] + " disconnected."
            })

    async def chat_message(self, event):
        """Called when someone has messaged in room"""
        print("PrivateChatConsumer", "chat_message")
        await self.send_json({
            "msg_type": MSG_TYPE_MESSAGE,
            "username": event["username"],
            "user_id": event["user_id"],
            "profile_image": event["profile_image"],
            "message": event["message"],
            "natural_timestamp": humanize_or_normal(timezone.now())
        })

    async def send_previous_messages(self, messages, new_page_number):
        """Sends previous messages to client"""
        print("PrivateChatConsumer", "send_previous_messages")

    async def send_user_info(self, user_details):
        """Sends the user details to the client"""
        print("PrivateChatConsumer", "send_user_info")
        await self.send_json({
            "user": user_details
        })

    async def handle_client_error(self, e: ClientError):
        """Called on ClientError"""
        error = {"error": e.code}
        if e.message:
            error["message"] = e.message
            await self.send_json(error)
