"""Websocket consumers for public_chat app"""

from django.utils import timezone
from django.contrib.auth import get_user_model

from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .models import PublicChatRoom
from .websockets import connect_user, disconnect_user, get_room_or_error, \
    chat_timestamp, create_new_public_room_chat
from utils.exceptions import ClientError

User = get_user_model()
MSG_TYPE_MESSAGE = 0


class PublicChatConsumer(AsyncJsonWebsocketConsumer):
    """Consumer to handle public chat"""

    async def connect(self):
        """Start the connection to client websocket"""
        print("PublicChat connect", self.scope["user"])
        await self.accept()

        # Store the room_id
        self.room_id = None

        # Add them to group
        await self.channel_layer.group_add(
            "public_chatroom_1",
            self.channel_name
        )

    async def disconnect(self, code):
        """Handle the close request from client websocket"""
        print("PublicChatConsumer", "disconnect")

        if self.room_id:
            await self.leave_room(self.room_id)

    async def receive_json(self, content, **kwargs):
        """Handle the data sent from the client websocket"""
        print("PublicChatConsumer", "receive_json", content)
        command: str = content.get("command", None)
        message: str = content.get("message", "")
        room_id = content.get("room_id")

        try:
            if command == "SEND":
                if not message.strip():
                    raise ClientError(422, "You can't send an empty message.")
                await self.send_room_message(room_id, message)
            elif command == "JOIN":
                await self.join_room(room_id)
            elif command == "LEAVE":
                await self.leave_room(room_id)
        except ClientError as e:
            await self.handle_client_error(e)

    async def send_room_message(self, room_id, message):
        """Called by receive_json when someone sends a message to a room"""
        print("PblicChatConsumer", "send_room_message")
        user = self.scope["user"]

        if self.room_id is not None:
            if str(room_id) != str(self.room_id):
                raise ClientError("ROOM_ACCESS_DENIED", "Room access denied")
            elif not user.is_authenticated:
                raise ClientError("AUTH_ERRO", "Not authenticated to join")
        else:
            raise ClientError("ROOM_ACCESS_DENIED", "Room access denied")

        room: PublicChatRoom = await get_room_or_error(room_id)
        await create_new_public_room_chat(room, user, message)
        await self.channel_layer.group_send(
            room.group_name,
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

    async def join_room(self, room_id):
        """Called by receive_json on JOIN command"""
        print("PublicChatConsumer", "join_room", self.scope["user"])
        if self.scope["user"].is_authenticated:
            try:
                room: PublicChatRoom = await get_room_or_error(room_id)
            except ClientError as e:
                await self.handle_client_error(e)
            else:
                # Add user to the room
                await connect_user(room, self.scope["user"])

                # Set the room_id with the current room
                self.room_id = room_id

                # Add user to the group
                await self.channel_layer.group_add(
                    room.group_name,
                    self.channel_name
                )

                # Send acknowledgement to client
                await self.send_json({
                    "join": str(room_id),
                    "username": self.scope["user"].username
                })

    async def leave_room(self, room_id):
        """Called by receive_json on LEAVE command"""
        print("PublicChatConsumer", "leave_room")
        if self.scope["user"].is_authenticated:
            try:
                room: PublicChatRoom = await get_room_or_error(room_id)
            except ClientError as e:
                await self.handle_client_error(e)
            else:
                # Remove user from room users
                await disconnect_user(room, self.scope["user"])

                # Set room_id to None
                self.room_id = None

                # Remove user from the group
                await self.channel_layer.group_discard(
                    room.group_name,
                    self.channel_name
                )

    async def handle_client_error(self, exception: ClientError):
        """Handle ClientError and send data to client"""
        error_data = {"error": exception.code}
        if exception.message:
            error_data["message"] = exception.message
            await self.send_json(error_data)
