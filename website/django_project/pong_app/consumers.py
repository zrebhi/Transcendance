import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from .pong import Game
from matchmaking.models import GameSession
from users.consumers import remove_channel_name_from_session, add_channel_name_to_session, update_user_session_id
from asgiref.sync import async_to_sync

FPS = 60
GLOBAL_GAMES_STORE = {}


def delete_game_for_session(session_id):
    """Delete a Game instance from the global store."""
    GLOBAL_GAMES_STORE.pop(session_id, None)


async def broadcast_message(group_name, message_data):
    """Broadcast a server-to-server message to all players. """
    channel_layer = get_channel_layer()
    await channel_layer.group_send(group_name, message_data)


def create_game_instance(session_id):
    game_session = GameSession.objects.select_related('player1', 'player2').get(id=session_id)
    GLOBAL_GAMES_STORE[session_id] = GameInstance(game_session=game_session)
    async_to_sync(GLOBAL_GAMES_STORE[session_id].start_game_tasks)()


async def create_game_instance_async(session_id):
    game_session = await get_game_session_async(session_id)
    GLOBAL_GAMES_STORE[session_id] = GameInstance(game_session=game_session)
    asyncio.create_task(GLOBAL_GAMES_STORE[session_id].start_game_tasks())


@database_sync_to_async
def get_game_session_async(session_id):
    return GameSession.objects.select_related('player1', 'player2').get(id=session_id)


@database_sync_to_async
def update_game_session_winner(session, winner_username):
    if session.winner is None:
        winner = session.player1 if session.player1.username == winner_username else session.player2
        session.winner = winner
        session.save()


@database_sync_to_async
def update_game_session_status(session, status):
    if session.status != status:
        session.status = status
        session.save()


class GameInstance:
    """Class to run the game loop and broadcast game state updates."""

    def __init__(self, game_session):
        self.game = Game(winning_score=3)
        self.game.session = game_session
        self.game_group_name = f'game_{self.game.session.id}'
        self.assign_players()

    def assign_players(self):
        """Assign the connected user to the appropriate player slot."""
        self.game.paddle1.player_name = self.get_player_name(1)
        self.game.paddle2.player_name = self.get_player_name(2)

    def get_player_name(self, player_number):
        """Determine the player name based on game type."""
        if self.game.session.mode == 'local':
            return f'Player {player_number}'
        return self.game.session.player1.username if player_number == 1 else self.game.session.player2.username

    async def start_game_tasks(self):
        """Start the game loop and game state broadcast tasks."""
        tasks = [self.run_game_loop('Ball'), self.run_game_loop('Paddles'), self.broadcast_game_state()]
        for task in tasks:
            asyncio.create_task(task)

    async def run_game_loop(self, target):
        """Run the main game loop, updating the game state."""
        while True:
            if target == 'Ball':
                await self.game.ball_loop()
            elif target == 'Paddles':
                await self.game.paddles_loop()
            await asyncio.sleep(1 / FPS)
            if self.game.status == 'finished':
                break

    async def broadcast_game_state(self):
        """Broadcast the current game state to all players."""
        while True:
            await broadcast_message(self.game_group_name,
                                    {'type': 'game_state_update', 'message': self.game.get_state()})
            await asyncio.sleep(1 / FPS)
            if self.game.status == 'finished':
                await broadcast_message(self.game_group_name, {'type': 'finished_message'})
                break


class GameConsumer(AsyncWebsocketConsumer):
    """Consumer for the game WebSocket."""

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.game = None
        self.game_group_name = None
        self.user = None

    async def connect(self):
        """Handle new WebSocket connection."""
        self.user = self.scope['user']
        self.game = await self.get_game_in_store()
        if self.game is None:
            await self.close()
            return
        await self.verify_user_in_game_session()
        await self.channel_setup()
        await self.update_game_status()

    async def get_game_in_store(self):
        """Retrieve or create a Game instance for the session ID."""
        game_session_id = self.scope['url_route']['kwargs']['game_session_id']
        if game_session_id not in GLOBAL_GAMES_STORE:
            await update_user_session_id(self.user, None)
            return None
        return GLOBAL_GAMES_STORE[game_session_id].game

    async def verify_user_in_game_session(self):
        """Verify if the connected user is part of the game session."""
        if self.user not in [self.game.session.player1, self.game.session.player2]:
            await self.close()
        await self.accept()

    async def channel_setup(self):
        """Set up the WebSocket connection."""
        self.game_group_name = f'game_{self.game.session.id}'
        await self.channel_layer.group_add(self.game_group_name, self.channel_name)
        await add_channel_name_to_session(self.scope, self.channel_name)

    async def update_game_status(self):
        """
        Update the game status to ongoing if both players are connected.
        We use two if statements to handle the case where both players are the same user in local games
        """
        if self.user == self.game.session.player1:
            self.game.paddle1.connected = True
            self.game.paddle1.pause_request = False
        if self.user == self.game.session.player2:
            self.game.paddle2.connected = True
            self.game.paddle2.pause_request = False

        if self.game.paddle1.connected and self.game.paddle2.connected:
            self.game.resume_game()

    def game_full(self):
        """Check if both player slots in the game are filled."""
        return None not in self.game.players

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        if self.game:
            self.handle_disconnect(self.user)
            await remove_channel_name_from_session(self.scope, self.channel_name)
        await self.close()

    def handle_disconnect(self, user):
        """Handle a player's disconnection."""
        if self.local_game():
            self.game.status = 'finished'
            return
        player_number = 1 if user == self.game.players[0] else 2
        self.game.players[player_number - 1] = None
        self.game.pause_request(player_number)

    async def receive(self, text_data=None, bytes_data=None):
        """Handle incoming messages from WebSocket."""
        if text_data:
            data = json.loads(text_data)
            if data.get('type') == "leave_message":
                await self.disconnect(1001)
            elif data.get('type') == "game_init_request":
                await self.send_game_init()
            elif data.get('type') == "move_command":
                self.handle_player_movement(data)
            elif data.get('type') == "forfeit_message":
                await self.handle_forfeit()
            elif data.get('type') == "quit_message" and self.local_game():
                await self.end_game()

    async def send_game_init(self):
        """Send initial game data to the WebSocket client."""
        init_message = self.game.get_initial_data(self.local_game())
        await self.send_json({'type': 'game_init', 'data': init_message})

    async def send_json(self, message):
        """Send a JSON message to the WebSocket client, handling any exceptions."""
        try:
            await self.send(text_data=json.dumps(message))
        except Exception as e:
            print(f"Error sending message: {e}")

    async def finished_message(self, event):
        if event and self.game.status == 'finished':
            await self.end_game()

    async def end_game(self):
        """End the game session and send the winner message."""
        await self.send_winner_message()
        delete_game_for_session(self.game.session.id)
        await self.disconnect(1001)
        for user in [self.game.session.player1, self.game.session.player2]:
            await update_user_session_id(user, None)
            await update_game_session_winner(self.game.session, self.game.winner)
            await update_game_session_status(self.game.session, 'finished')

    async def game_state_update(self, event):
        """Send game state updates to the WebSocket client."""
        await self.send_json({'type': 'game_state', 'data': event['message']})

    async def send_winner_message(self):
        """Send the winner message to the WebSocket client."""
        await self.game_state_update({'message': self.game.get_state()})
        await self.send_json({'type': 'winner_message', 'winner': self.game.winner})

    def handle_player_movement(self, data):
        if self.local_game():
            player_number = 1 if 'player1' in data['message'] else 2 if 'player2' in data['message'] else None
        else:
            player_number = 1 if self.user == self.game.session.player1 else 2
        direction = 'up' if 'move_up' in data['message'] else 'down'
        self.queue_player_movement(player_number, direction)

    def queue_player_movement(self, player_number, direction):
        """Add a player movement command to the queue,
        so that we can process them all on the next frame."""
        self.game.move_commands.append((player_number, direction))

    def local_game(self):
        """Check if the game is a local game."""
        return self.game.session.player1 == self.game.session.player2

    async def handle_forfeit(self):
        """Handle a player's forfeit."""
        self.game.winner = self.game.session.player1.username if self.user == self.game.session.player2 \
            else self.game.session.player2.username
        await broadcast_message(self.game_group_name, {'type': 'forfeit_notification',
                                                       'message': f'{self.user.username} has forfeited the game'})
        self.game.status = 'finished'

    async def forfeit_notification(self, event):
        """Send a forfeit notification to the WebSocket client."""
        await self.send_json({'type': 'forfeit_notification', 'message': event['message']})
