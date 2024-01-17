import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Game
from matchmaking.models import GameSession
from users.consumers import remove_channel_name_from_session, add_channel_name_to_session

FPS = 60
GLOBAL_GAMES_STORE = {}


def get_game_for_session(session_id):
    """Retrieve or create a Game instance for the session ID."""
    GLOBAL_GAMES_STORE.setdefault(session_id, Game(winning_score=10))
    return GLOBAL_GAMES_STORE[session_id]


def delete_game_for_session(session_id):
    """Delete a Game instance from the global store."""
    GLOBAL_GAMES_STORE.pop(session_id, None)


class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.initialize_variables()
        if not await self.verify_user_in_game_session():
            return
        await self.setup_connection()
        self.assign_players()
        self.start_game_tasks()

    def initialize_variables(self):
        """Initialize necessary variables for the WebSocket connection."""
        self.game_session_id = self.scope['url_route']['kwargs']['game_session_id']
        self.game_group_name = f'game_{self.game_session_id}'
        self.user = self.scope["user"]

    async def verify_user_in_game_session(self):
        """Verify if the connected user is part of the game session."""
        self.game_session = await self.get_game_session_async(self.game_session_id)
        if self.user not in [self.game_session.player1, self.game_session.player2]:
            await self.close()
            return False
        return True

    @database_sync_to_async
    def get_game_session_async(self, session_id):
        """Retrieve a GameSession object asynchronously."""
        return GameSession.objects.select_related('player1', 'player2').get(id=session_id)

    async def setup_connection(self):
        """Set up the WebSocket connection."""
        await self.accept()
        await self.channel_layer.group_add(self.game_group_name, self.channel_name)
        await self.update_user_session_id(self.game_session_id)
        await add_channel_name_to_session(self.scope, self.channel_name)
        self.game = get_game_for_session(self.game_session_id)

    @database_sync_to_async
    def update_user_session_id(self, new_session_id):
        """Update the user's session_id in the database."""
        self.user.session_id = new_session_id
        self.user.save()

    def assign_players(self):
        """Assign the connected user to the appropriate player slot."""
        if self.user == self.game_session.player1:
            self.game.players[0] = self.user
            self.game.paddle1.player_name = self.get_player_name(1)
        if self.user == self.game_session.player2:
            self.game.players[1] = self.user
            self.game.paddle2.player_name = self.get_player_name(2)

    def get_player_name(self, player_number):
        """Determine the player name based on game type."""
        return self.user.username if not self.local_game() else f'Player {player_number}'

    def start_game_tasks(self):
        """Start background tasks for running and broadcasting the game."""
        if self.game.status == 'pending':
            asyncio.create_task(self.run_game_loop('Ball'))
            asyncio.create_task(self.run_game_loop('Paddles'))
            asyncio.create_task(self.broadcast_game_state())
            self.game.status = 'awaiting players'
        if self.game_full():
            self.game.status = 'ongoing'

    def game_full(self):
        """Check if both player slots in the game are filled."""
        return None not in self.game.players

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
            await self.broadcast_message({'type': 'game_state_update', 'message': self.game.get_state()})
            await asyncio.sleep(1 / FPS)
            if self.game.status == 'finished':
                await self.broadcast_message({'type': 'finished_message'})
                break

    async def broadcast_message(self, message_data):
        """Broadcast a server-to-server message to all players. """
        await self.channel_layer.group_send(self.game_group_name, message_data)

    async def game_state_update(self, event):
        """Send game state updates to the WebSocket client."""
        await self.send_json({'type': 'game_state', 'data': event['message']})

    async def finished_message(self, event):
        if self.game.status == 'finished':
            await self.end_game()

    async def end_game(self):
        """End the game session and send the winner message."""
        await self.send_winner_message()
        await self.update_user_session_id(None)
        await self.disconnect(1001)

    async def send_json(self, message):
        """Send a JSON message to the WebSocket client, handling any exceptions."""
        try:
            await self.send(text_data=json.dumps(message))
        except Exception as e:
            print(f"Error sending message: {e}")

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        self.handle_disconnect(self.user)
        await remove_channel_name_from_session(self.scope, self.channel_name)
        await self.close()
        if self.game.status == 'finished':
            delete_game_for_session(self.game_session_id)

    def handle_disconnect(self, user):
        """Handle a player's disconnection."""
        if self.game.status != 'finished':
            self.game.status = 'paused'
        if user == self.game.players[0]:
            self.game.players[0] = None
        if user == self.game.players[1]:
            self.game.players[1] = None

    async def receive(self, text_data):
        """Handle incoming messages from WebSocket."""
        data = json.loads(text_data)
        if data.get('type') == "leave_message":
            await self.disconnect(1001)
        elif data.get('type') == "game_init_request":
            await self.send_game_init() if self.game_full() else None
        elif data.get('type') == "move_command":
            self.handle_player_movement(data)
        elif data.get('type') == "forfeit_message":
            await self.handle_forfeit(data)

    async def send_winner_message(self):
        """Send the winner message to the WebSocket client."""
        await self.game_state_update({'message': self.game.get_state()})
        await self.send_json({'type': 'winner_message', 'winner': self.game.winner})

    async def send_game_init(self):
        """Send initial game data to the WebSocket client."""
        init_message = self.game.get_initial_data(self.local_game())
        await self.send_json({'type': 'game_init', 'data': init_message})

    def handle_player_movement(self, data):
        if self.local_game():
            player_number = 1 if 'player1' in data['message'] else 2 if 'player2' in data['message'] else None
        else:
            player_number = 1 if self.user == self.game_session.player1 else 2
        direction = 'up' if 'move_up' in data['message'] else 'down'
        self.queue_player_movement(player_number, direction)

    def queue_player_movement(self, player_number, direction):
        """Add a player movement command to the queue,
        so that we can process them all on the next frame."""
        self.game.move_commands.append((player_number, direction))

    def local_game(self):
        """Check if the game is a local game."""
        return self.game_session.player1 == self.game_session.player2

    async def handle_forfeit(self, data):
        """Handle a player's forfeit."""
        self.game.winner = self.game_session.player1.username if self.user == self.game_session.player2 \
            else self.game_session.player2.username
        await self.broadcast_message({'type': 'forfeit_notification',
                                      'message': f'{self.user.username} has forfeited the game'})
        self.game.status = 'finished'

    async def forfeit_notification(self, event):
        """Send a forfeit notification to the WebSocket client."""
        await self.send_json({'type': 'forfeit_notification', 'message': event['message']})
