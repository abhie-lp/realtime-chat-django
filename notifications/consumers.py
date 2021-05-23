"""Wesocket consumer for notifications app"""

from channels.generic.websocket import AsyncJsonWebsocketConsumer


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    """AsyncConsumer for sending friend request and chat notifications"""

    async def connect(self):
        """Initiate the handshake and accept incoming connection"""
        print("NotificationConsumer: connect:", self.scope["user"])
        await self.accept()

    async def disconnect(self, code):
        """Called when websocket disconnects"""
        print("NotificationConsumer: disconnect")

    async def receive_json(self, content, **kwargs):
        """Called when data is send from client to server"""
        command = content.get("command")
        print("NotificationConsumer: receive_json", command)
