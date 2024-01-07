from channels.generic.websocket import AsyncWebsocketConsumer
from .matchmaking import match_users
import json

class QueueConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for the game matchmaking queue.
    """

    async def connect(self):
        # Assign a unique group for each user
        self.user = self.scope["user"]
        self.room_group_name = f'queue_{self.user.id}'

        # Add to group and accept the connection
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Initiate the matchmaking process
        await match_users()

    async def disconnect(self, close_code):
        # Remove from group on disconnect
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.close()

    async def game_matched(self, data):
        """
        Sends a game_matched message to the WebSocket.
        This is triggered when a game session is successfully created for the user.
        """
        await self.send(text_data=json.dumps({
            'type': 'game_matched',
            'session_id': data['message']['session_id']
        }))
        await self.close()
