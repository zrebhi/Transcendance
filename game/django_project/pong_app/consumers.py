# consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from pong_app.models import Window, Game
import asyncio


class GameConsumer(AsyncWebsocketConsumer):
    window = Window(width=1200, height=900)
    game = Game(window)
    closed_socket = False
    FPS = 60

    async def connect(self):
        if self.is_game_full():
            return
        await self.accept_and_assign_player()
        self.manage_game_state_on_connection()
        self.start_game_tasks()
        print(self.game.players)

    def is_game_full(self):
        return self.game.players[0] is not None and self.game.players[1] is not None

    async def accept_and_assign_player(self):
        if self.game.players[0] is None:
            self.game.players[0] = self.channel_name
        else:
            self.game.players[1] = self.channel_name
        await self.accept()

    def manage_game_state_on_connection(self):
        if self.game.players[0] is not None and self.game.players[1] is not None:
            self.game.pause_game = False

    def start_game_tasks(self):
        if not self.game.running:
            self.game.running = True
            asyncio.create_task(self.run_game_loop())
        asyncio.create_task(self.send_game_state())

    async def disconnect(self, close_code):
        self.remove_player_and_close()
        await self.close()
        print(self.game.players)

    def remove_player_and_close(self):
        player_index = self.get_player_index()
        if player_index is not None:
            self.game.players[player_index] = None
            self.game.pause_game = True
            self.closed_socket = True

    def get_player_index(self):
        for index, channel_name in self.game.players.items():
            if channel_name == self.channel_name:
                return index
        return None

    async def receive(self, text_data):
        data = json.loads(text_data)
        self.handle_player_movement(data['message'])

    def handle_player_movement(self, message):
        if message in ['move_up_player', 'move_down_player']:
            player_number = 1 if self.game.players[0] == self.channel_name else 2
            direction = 'up' if message == 'move_up_player' else 'down'
            self.game.move_player(player_number, direction)

    async def run_game_loop(self):
        while True:
            self.game.loop()
            await asyncio.sleep(1 / self.FPS)

    async def send_game_state(self):
        while not self.closed_socket:
            await self.send(text_data=json.dumps(self.game.get_state()))
            await asyncio.sleep(1 / self.FPS)
