"""Wesocket consumer for notifications app"""

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .constants import GENERAL_NOTIFICATON
from notifications import websocket


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
        user = self.scope["user"]
        if not user.is_authenticated:
            self.send_json({
                "error": "Not authenticated"
            })
            await self.disconnect()
        command = content.get("command")
        match command:
            case "general_notifications":
                if (payload := await websocket.general_notifications(self.scope["user"], content["page_number"])):
                    await self.send_general_notifications(payload)
                else:
                    await self.send_json({
                        "error": "Something went wrong"
                    })
        print("NotificationConsumer: receive_json", command)
    
    async def send_general_notifications(self, payload: dict):
        payload["type"] = GENERAL_NOTIFICATON
        return await self.send_json(payload)
