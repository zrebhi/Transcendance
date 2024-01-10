import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from pong_app.models import Window, Game
from matchmaking.models import GameSession

FPS = 60
GLOBAL_GAMES_STORE = {}

# Utility functions to manage the global games store
def get_game_for_session(session_id):
    """Retrieve or create a Game instance for a given session ID."""
    if session_id not in GLOBAL_GAMES_STORE:
        GLOBAL_GAMES_STORE[session_id] = Game(Window(width=1200, height=900))
    return GLOBAL_GAMES_STORE[session_id]

def delete_game_for_session(session_id):
    """Delete a Game instance from the global store for a given session ID."""
    if session_id in GLOBAL_GAMES_STORE:
        del GLOBAL_GAMES_STORE[session_id]

# Game consumer handling WebSocket connections for game sessions
class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handle new WebSocket connection."""
        self.game_session_id = self.scope['url_route']['kwargs']['game_session_id']
        self.game_group_name = f'game_{self.game_session_id}'
        self.user = self.scope["user"]

        # Retrieve the game session and verify the user's participation
        self.game_session = await self.get_game_session_async(self.game_session_id)
        if self.user not in [self.game_session.player1, self.game_session.player2]:
            await self.close()
            return

        # Join the game group for broadcasting messages
        await self.accept()
        await self.channel_layer.group_add(self.game_group_name, self.channel_name)
        self.closed_socket = False

        # Add the channel name to the user's session so we can close it on logout
        await self.add_channel_name_to_session(self.channel_name)


        # Initialize or retrieve the game instance
        self.game = get_game_for_session(self.game_session_id)
        self.assign_player()
        self.manage_game_state_on_connection()

    @database_sync_to_async
    def get_game_session_async(self, session_id):
        """Asynchronously retrieve a GameSession object."""
        try:
            return GameSession.objects.select_related('player1', 'player2').get(id=session_id)
        except GameSession.DoesNotExist:
            return None

    @database_sync_to_async
    def add_channel_name_to_session(self, channel_name):
        """Add the channel name to an array in the session so we can close them on logout."""
        session = self.scope["session"]
        if "channel_names" not in session:
            session["channel_names"] = []
        if channel_name not in session["channel_names"]:
            session["channel_names"].append(channel_name)
            # Mark the session as modified to ensure the changes are saved
            # in the async context
            session.modified = True
            session.save()

    def assign_player(self):
        """Assign the connected user to a player slot in the game."""
        if self.user == self.game_session.player1:
            self.game.players[0] = self.user
        else:
            self.game.players[1] = self.user

    def manage_game_state_on_connection(self):
        """Manage the game state when a player connects."""
        if not self.is_game_full():
            self.game.pause_game = True
            self.start_game_tasks()
        else:
            self.game.pause_game = False

    def is_game_full(self):
        """Check if both player slots in the game are filled."""
        return self.game.players[0] is not None and self.game.players[1] is not None

    def start_game_tasks(self):
        """Start background tasks for running and broadcasting the game."""
        if not self.game.running:
            self.game.running = True
            asyncio.create_task(self.run_game_loop())
        asyncio.create_task(self.broadcast_game_state())

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        self.game.pause_game = True
        self.closed_socket = True
        if self.user == self.game_session.player1:
            self.game.players[0] = None
        else:
            self.game.players[1] = None
        await self.remove_channel_name_from_session(self.channel_name)
        await self.close()

    @database_sync_to_async
    def remove_channel_name_from_session(self, channel_name):
        """Removes the channel name from the session."""
        session = self.scope["session"]
        try:
            if "channel_names" in session and channel_name in session["channel_names"]:
                session["channel_names"].remove(channel_name)
                session.modified = True
                session.save()
        except Exception as e:
            # Handle exceptions, such as session not existing or save errors
            print(f"Error updating session: {e}")
    async def leave_message(self, event):
        """Message sent by the server when the user logs out."""
        await self.disconnect(1001)

    async def receive(self, text_data):
        """Receive and handle messages from WebSocket."""
        data = json.loads(text_data)
        self.handle_player_movement(data['message'])

    def handle_player_movement(self, message):
        """Handle player movement commands."""
        player_number = 1 if self.game.players[0] == self.user else 2
        direction = 'up' if message == 'move_up_player' else 'down'
        self.game.move_player(player_number, direction)

    async def run_game_loop(self):
        """Run the game loop, updating the game state."""
        while True:
            self.game.loop()
            await asyncio.sleep(1 / FPS)

    async def broadcast_game_state(self):
        """Broadcast the game state to all players in the game group."""
        while not self.closed_socket:
            await self.channel_layer.group_send(
                self.game_group_name,
                {
                    'type': 'game_state_update',
                    'message': self.game.get_state()
                }
            )
            await asyncio.sleep(1 / FPS)

    async def game_state_update(self, event):
        """
        Receive game state updates and send them to the WebSocket client.
        """
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'game_state',
            'data': event['message']
        }))