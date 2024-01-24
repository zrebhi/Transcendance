import json
from channels.generic.websocket import AsyncWebsocketConsumer


class TournamentConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.tournament_id = None
        self.tournament_group_name = None

    async def connect(self):
        self.user = self.scope["user"]
        if self.user.tournament_id is None:
            await self.close()
            return
        self.tournament_group_name = f'tournament_{self.user.tournament_id}'

        # Join tournament group
        await self.channel_layer.group_add(
            self.tournament_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave tournament group
        await self.channel_layer.group_discard(
            self.tournament_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']

            # Send message to tournament group
            await self.channel_layer.group_send(
                self.tournament_group_name,
                {
                    'type': 'tournament_message',
                    'message': message
                }
            )

    # Receive message from tournament group
    async def tournament_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
