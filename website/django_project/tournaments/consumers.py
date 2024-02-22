import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import TournamentMatch, MatchParticipant
from pong_app.consumers import broadcast_message, create_game_instance
from matchmaking.models import GameSession
from users.consumers import add_channel_name_to_session, remove_channel_name_from_session


class TournamentConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.tournament_id = None
        self.tournament_group_name = None
        self.game_session = None

    async def connect(self):
        self.user = self.scope["user"]
        if self.user.tournament_id is None:
            await self.close()
            return
        self.tournament_group_name = f'tournament_{self.user.tournament_id}'

        # Join tournament group
        await self.channel_layer.group_add(self.tournament_group_name, self.channel_name)
        # Join user group for individualized communication
        await self.channel_layer.group_add(self.user.username, self.channel_name)
        # Adds the channel to the user's session, so we can close it on user logout
        await add_channel_name_to_session(self.scope, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave tournament group
        await self.channel_layer.group_discard(self.tournament_group_name, self.channel_name)
        await self.channel_layer.group_discard(self.user.username, self.channel_name)
        # Remove the channel from the user's session
        await remove_channel_name_from_session(self.scope, self.channel_name)
        await self.close()

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            message = json.loads(text_data)

            if message['type'] == 'ready_state_update':
                print(f"Received ready state update: {message['ready_state']}")
                await self.update_match_participant_ready_state(message['match_id'], message['ready_state'])
                print(f"Updated ready state for match {message['match_id']} to {message['ready_state']}")
                if not await self.check_and_start_match(message['match_id']):
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

    async def check_and_start_match(self, match_id):
        try:
            match = await self.get_match(match_id)
            if await self.all_participants_ready(match):
                await self.update_match_status(match, 'in progress')
                await self.create_game_for_match(match)
                await self.notify_match_participants(match)
                await broadcast_message(self.tournament_group_name, {'type': 'tournament_message',
                                                                     'message': 'match_start'})
                return True
            return False

        except TournamentMatch.DoesNotExist as e:
            print(f"Error: {str(e)}")
            return False

    @database_sync_to_async
    def get_match(self, match_id):
        return TournamentMatch.objects.get(id=match_id)

    @database_sync_to_async
    def all_participants_ready(self, match):
        return all(participant.is_ready for participant in match.participants.all())

    @database_sync_to_async
    def update_match_status(self, match, status):
        match.status = status
        match.save()

    @database_sync_to_async
    def create_game_for_match(self, match):
        self.game_session = GameSession.objects.create(
            player1=match.participants.first().player,
            player2=match.participants.last().player,
            mode='tournament')
        create_game_instance(self.game_session.id)
        match.game_session = self.game_session
        match.save()

    async def notify_match_participants(self, match):
        participants = await self.get_match_participants(match)
        for participant in participants:
            await broadcast_message(participant.player.username, {'type': 'user_message',
                                                                  'message': 'game_start'})
            await self.update_user_session_id(participant.player, self.game_session.id)

    @database_sync_to_async
    def get_match_participants(self, match):
        """
        Retrieve all participants in a match.
        Django's database operations are lazy meaning that they are not executed until they are needed.
        This is why we need to convert the QuerySet to a list to ensure that the database is accessed inside this
        function.
        """
        return list(match.participants.select_related('player').all())

    @database_sync_to_async
    def update_user_session_id(self, user, session_id):
        user.session_id = session_id
        user.save()

    # Receive message from tournament group
    async def tournament_message(self, event):
        message = event['message']

        print(f"Received message: {message}")
        try:
            print(f"Sending message: {message}")
            await self.send(text_data=json.dumps({
                'type': 'tournament_message',
                'message': message
            }))
            print(f"Sent message: {message}")
        except Exception as e:
            print(f"Error: {str(e)}")

    async def user_message(self, event):
        message = event['message']
        # Send message to WebSocket
        if message == 'game_start':
            await self.send(text_data=json.dumps({
                'type': 'game_start',
                'session_id': self.game_session.id
            }))

    async def leave_message(self, event):
        if event:
            await self.disconnect(1001)
