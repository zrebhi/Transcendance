from channels.generic.websocket import AsyncWebsocketConsumer
from .models import QueueEntry
from .matchmaking import match_users
import asyncio
import json

class QueueConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.room_group_name = f'queue_{self.user.id}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        print(f'{self.room_group_name}: Added to group')
        await self.accept()
        asyncio.create_task(match_users())

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        print(f'{self.room_group_name}: Removed from group')
        await self.close()

    async def receive(self, text_data):
        data = json.loads(text_data)
        event_type = data.get('type')

        if event_type == 'game_matched':
            await self.game_matched(data)
        # Add more conditions for other types of messages/events
        else:
            print(f"Received unknown event type: {event_type}")

    async def game_matched(self, data):
        # Process the 'game_matched' event
        try:
            print(f"{self.room_group_name}: Processing 'game_matched' with data: {data}")
            # Additional processing logic here
            # For example, you might want to send a message back to the client
            await self.send(text_data=json.dumps({
                'type': 'game_matched',
                'data': data['message']
            }))
            print(f"{self.room_group_name}: Sent 'game_matched' message to WebSocket")
        except Exception as e:
            print(f"Error in game_matched for {self.room_group_name}: {e}")
