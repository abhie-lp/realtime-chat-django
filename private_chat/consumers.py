"""Websocket consumers for private_chat app"""

from channels.generic.websocket import AsyncJsonWebsocketConsumer


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

        if command == "JOIN":
            pass
        elif command == "LEAVE":
            pass
        elif command == "SEND":
            pass
        elif command == "ROOM_CHATS":
            pass

    async def disconnect(self, code):
        """Called when websocket closes"""
        print("PrivateChatConsumer", "disconnect")
        pass

    async def join_room(self, room_id):
        """Called when JOIN command is received in receive_json"""
        print("PrivateChatConsumer", "join_room", room_id)

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
