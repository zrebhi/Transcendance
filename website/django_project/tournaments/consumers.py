import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import TournamentMatch, MatchParticipant
from pong_app.consumers import broadcast_message


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

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            message = json.loads(text_data)

            if message['type'] == 'ready_state_update':
                await self.update_match_participant_ready_state(message['match_id'], message['ready_state'])
                await broadcast_message(self.tournament_group_name, {'type': 'tournament_message',
                                                                     'message': 'ready_state_updated'})

    @database_sync_to_async
    def update_match_participant_ready_state(self, match_id, ready_state):
        try:
            match = TournamentMatch.objects.get(id=match_id)
            participant = match.participants.get(player=self.scope["user"])
            participant.is_ready = ready_state == "ready"
            participant.save()
        except (MatchParticipant.DoesNotExist, TournamentMatch.DoesNotExist) as e:
            print(f"Error: {str(e)}")

    # Receive message from tournament group
    async def tournament_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'tournament_message',
            'message': message
        }))
