"""Wesocket consumer for notifications app"""

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from notifications import constants as c
from notifications import websocket


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    """AsyncConsumer for sending friend request and chat notifications"""

    async def connect(self):
        """Initiate the handshake and accept incoming connection and create the group for user"""
        user = self.scope["user"]
        print("NotificationConsumer: connect:", user)
        if user.is_authenticated:
            await self.channel_layer.group_add(f"{user.id}", self.channel_name)
            await self.accept()
        else:
            self.close()

    async def disconnect(self, code):
        """Called when websocket disconnects"""
        print("NotificationConsumer: disconnect")
        await self.channel_layer.group_discard(
            f"{self.scope['user'].id}", self.channel_name
        )

    async def receive_json(self, content, **kwargs):
        """Called when data is send from client to server"""
        user = self.scope["user"]
        if not user.is_authenticated:
            self.send_json({"error": "Not authenticated"})
            await self.disconnect()
        command = content.get("command")
        match command:
            case "general_notifications":
                if payload := await websocket.general_notifications(
                    self.scope["user"], content["page_number"]
                ):
                    await self.send_general_notifications(payload)
                else:
                    await self.send_json({"error": "Something went wrong"})
            case "read":
                await websocket.mark_notification_read(content.get("notification"))
            case "ping":
                self.send_json({"type": "pong"})
        print("NotificationConsumer: receive_json", command)

    async def send_general_notifications(self, payload: dict):
        print("Send general notifications")
        payload["type"] = c.GENERAL_NOTIFICATONS
        await self.send_json(payload)

    async def send_single_notification(self, payload: dict):
        print("Send single notification")
        payload["type"] = c.GENERAL_SINGLE_NOTIFICATION
        await self.send_json(payload)
