# consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from pong_game.models import Window, Game
import asyncio


class GameConsumer(AsyncWebsocketConsumer):

    window = Window(width=1200, height=900)
    game = Game(window)

    async def connect(self):
        if len(self.game.players) == 2:
            return
        await self.accept()

        self.game.players[len(self.game.players)] = self.channel_name
        print(self.game.players)
        if len(self.game.players) >= 2:
            self.game.pause_game = 0

        asyncio.create_task(self.run_game())

        await self.send(text_data=json.dumps(self.game.get_state()))

    async def disconnect(self, close_code):
        # Remove player from the dictionary when disconnected
        player_index = None
        for index, channel_name in self.game.players.items():
            if channel_name == self.channel_name:
                player_index = index
                break

        if player_index is not None:
            self.game.players.pop(player_index)
            self.game.players = {i: channel_name for i, channel_name in enumerate(self.game.players.values())}
            print(self.game.players)
            if player_index <= 1:
                self.game.pause_game = 1
        await self.close()

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']

        print(message)

        if message == 'get_initial_data':
            await self.send(text_data=json.dumps(self.game.get_state()))
            return

        elif message == 'move_up_player':
            if self.game.players[0] == self.channel_name:
                self.game.move_player(1, "up")
            elif self.game.players[1] == self.channel_name:
                self.game.move_player(2, "up")
        elif message == 'move_down_player':
            if self.game.players[0] == self.channel_name:
                self.game.move_player(1, "down")
            elif self.game.players[1] == self.channel_name:
                self.game.move_player(2, "down")
        # Send updated player and ball positions to all connected clients
        await self.send(text_data=json.dumps(self.game.get_state()))

    async def run_game(self):
        while True:
            self.game.loop()
            await self.send(text_data=json.dumps(self.game.get_state()))
            await asyncio.sleep(1/120)
