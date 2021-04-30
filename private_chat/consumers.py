"""Websocket consumers for private_chat app"""

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from utils.exceptions import ClientError
from .websockets import get_user_info, get_room_or_error


class PrivateChatConsumer(AsyncJsonWebsocketConsumer):
    """Chat consumer"""

    async def connect(self):
        """Initiating the handshake."""
        print("PrivateChatConsumer", "connect", self.scope["user"])

        await self.accept()

        # room_id acts as a check if connected or else None.
        self.room_id = None

    async def receive_json(self, content, **kwargs):
        """
        Called when receiving a message.
        Check the content to process further
        """

        print("PrivateChatConsumer", "receive_json")
        command = content.get("command", None)
        room_id = content.get("room_id")
        logged_user = self.scope["user"]

        try:
            if command == "JOIN":
                await self.join_room(room_id)
            elif command == "LEAVE":
                pass
            elif command == "SEND":
                pass
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
        pass

    async def join_room(self, room_id):
        """Called when JOIN command is received in receive_json"""
        print("PrivateChatConsumer", "join_room", room_id)
        room = await get_room_or_error(room_id, self.scope["user"])
        await self.send_json({
            "join": room.id
        })

    async def leave_room(self, room_id):
        """Called when LEAVE command is received in receive_json"""
        print("PrivateChatConsumer", "leave_room", room_id)

    async def send_room(self, room_id, message):
        """Called in receive_json to send a message to room_id"""
        print("PrivateChatConsumer", "send_json", room_id)

    async def chat_join(self, event):
        """Called when someone has joined the chat"""
        print("PrivateChatConsumer", "chat_join", self.scope["user"])

    async def chat_leave(self, event):
        """Called when someone leaves the chat"""
        print("PrivateChatConsumer", "chat_leave")

    async def chat_message(self, event):
        """Called when someone has messaged in room"""
        print("PrivateChatConsumer", "chat_message")

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
