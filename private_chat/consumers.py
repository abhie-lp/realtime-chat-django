"""Websocket consumers for private_chat app"""

from django.utils import timezone
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from utils.exceptions import ClientError
from utils.timestamp import humanize_or_normal

from .constants import MSG_TYPE_ENTER, MSG_TYPE_LEAVE, MSG_TYPE_MESSAGE
from account.models import Account
from .websockets import (
    get_user_info,
    get_room_or_error,
    create_new_private_chat,
    get_private_room_chat_messages,
)


class PrivateChatConsumer(AsyncJsonWebsocketConsumer):
    """Chat consumer"""

    async def connect(self):
        """Initiating the handshake."""
        self.user: Account = self.scope["user"]
        print("PrivateChatConsumer", "connect", self.user)
        if not self.user.is_authenticated:
            self.close()
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
        print("PrivateChatConsumer", "receive_json", command, room_id)
        try:
            match command:
                case "JOIN":
                    await self.join_room(room_id)
                case "PRESENT":  # The other friend informs it's online presence
                    await self.join_room(room_id, present=True)
                case "LEAVE":
                    await self.leave_room(room_id)
                case "SEND":
                    if len(content["message"].lstrip()) != 0:
                        await self.send_room(room_id, content["message"])
                case "ROOM_CHATS":
                    payload: dict = await get_private_room_chat_messages(
                        await get_room_or_error(room_id, self.user),
                        content["page_number"],
                    )
                    await self.send_previous_messages(payload)
                case "USER_INFO":
                    room = await get_room_or_error(room_id, self.user)
                    user_info = await get_user_info(room, self.user)
                    await self.send_user_info(user_info)
        except ClientError as e:
            await self.handle_client_error(e)

    async def disconnect(self, code):
        """Called when websocket closes"""
        print("PrivateChatConsumer", "disconnect")
        if self.room:
            await self.leave_room(self.room.id)
        self.close()

    async def join_room(self, room_id, present=False):
        """Called when JOIN command is received in receive_json"""
        print("PrivateChatConsumer", "join_room", room_id)
        self.room = await get_room_or_error(room_id, self.user)

        # Add to the group
        await self.channel_layer.group_add(self.room.group_name, self.channel_name)

        await self.send_json({"join": room_id})
        await self.channel_layer.group_send(
            self.room.group_name,
            {
                "type": "chat.join",
                # "room_id": self.room.id,
                "username": self.user.username,
                "present": present
            },
        )

    async def leave_room(self, room_id):
        """Called when LEAVE command is received in receive_json"""
        print("PrivateChatConsumer", "leave_room", room_id)

        await self.channel_layer.group_send(
            self.room.group_name,
            {
                "type": "chat.leave",
                # "room_id": self.room.id,
                "username": self.user.username,
            },
        )
        await self.channel_layer.group_discard(self.room.group_name, self.channel_name)
        self.room = None
        await self.send_json({"leave": room_id})

    async def send_room(self, room_id, message):
        """Called in receive_json to send a message to private room"""
        print("PrivateChatConsumer", "send_json", room_id)
        if self.room is not None and self.room.id == room_id:
            user = self.user

            # Store the message in DB
            await create_new_private_chat(self.room, user, message)

            # Transfer the message to client and other user
            await self.channel_layer.group_send(
                self.room.group_name,
                {
                    "type": "chat.message",
                    "username": user.username,
                    "user_id": user.id,
                    "profile_image": (
                        user.profile_image.url if user.profile_image else None
                    ),
                    "message": message,
                },
            )
        else:
            raise ClientError("ROOM_ACCESS_DENIED", "Room access denied")

    async def chat_join(self, event: dict):
        """Called when someone has joined the chat"""
        print("PrivateChatConsumer", "chat_join", self.user)
        if event["username"] != self.user.username:
            event["msg_type"] = MSG_TYPE_ENTER
            await self.send_json(event)

    async def chat_leave(self, event):
        """Called when someone leaves the chat"""
        print("PrivateChatConsumer", "chat_leave")
        if event["username"] != self.user.username:
            event["msg_type"] = MSG_TYPE_LEAVE
            await self.send_json(event)

    async def chat_message(self, event):
        """Called when someone has messaged in room"""
        print("PrivateChatConsumer", "chat_message")
        event["msg_type"] = MSG_TYPE_MESSAGE
        event["natural_timestamp"] = humanize_or_normal(timezone.now())
        await self.send_json(event)

    async def send_previous_messages(self, payload: dict):
        """Sends previous messages to client"""
        print("PrivateChatConsumer", "send_previous_messages")
        payload["messages_payload"] = "previous_messages"
        await self.send_json(payload)

    async def send_user_info(self, user_details):
        """Sends the user details to the client"""
        print("PrivateChatConsumer", "send_user_info")
        await self.send_json({"user": user_details})

    async def handle_client_error(self, e: ClientError):
        """Called on ClientError"""
        error = {"error": e.code}
        if e.message:
            error["message"] = e.message
            await self.send_json(error)
