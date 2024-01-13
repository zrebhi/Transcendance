import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import QueueEntry
from .matchmaking import match_users
from pong_app.consumers import remove_channel_name_from_session


class QueueConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer that handles the matchmaking queue logic."""

    async def connect(self):
        """
        Handle new WebSocket connection.
        Assigns a unique group for each user and initiates the matchmaking process.
        """
        # Assign a unique group based on the user's ID to manage matchmaking
        self.user = self.scope["user"]
        self.room_group_name = f'queue_{self.user.id}'

        # Add the user to their group and accept the WebSocket connection
        await self.accept()
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.add_channel_name_to_session(self.channel_name)

        # Start matchmaking process
        await match_users()

    @database_sync_to_async
    def add_channel_name_to_session(self, channel_name):
        """Add the channel name to an array in the session."""
        session = self.scope["session"]
        if "channel_names" not in session:
            session["channel_names"] = []
        if channel_name not in session["channel_names"]:
            session["channel_names"].append(channel_name)
            session.modified = True
            session.save()

    async def disconnect(self, close_code):
        """
        Handle disconnection of WebSocket.
        Removes the user from the matchmaking group and deletes their queue entry.
        """
        # Remove the user from their matchmaking group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        await remove_channel_name_from_session(self.scope, self.channel_name)
        # Remove the user's entry from the matchmaking queue
        await self.delete_queue_entry()
        await self.close()
        print(f"disconnected from {self.room_group_name}")

    @database_sync_to_async
    def delete_queue_entry(self):
        """
        Deletes the user's queue entry from the database.
        This method is an asynchronous database operation.
        """
        QueueEntry.objects.filter(user=self.user).delete()

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')

        if message_type == 'leave_message':
            await self.leave_message(self)

    async def leave_message(self, event):
        await self.disconnect(1001)

    async def game_matched(self, data):
        """
        Notify the user when a game match is found.
        Sends a message to the WebSocket client with the session ID of the matched game.
        """
        await self.send(text_data=json.dumps({
            'type': 'game_matched',
            'session_id': data['message']['session_id']
        }))
        await self.close()
