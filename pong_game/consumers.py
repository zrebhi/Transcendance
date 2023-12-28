# consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from pong_game.models import Player, Ball, Window
from channels.layers import get_channel_layer

class GameConsumer(AsyncWebsocketConsumer):
    players = {}  # Dictionary to track players

    async def connect(self):
        await self.accept()

        self.players[len(self.players)] = self.channel_name
        print(self.players)

        self.window = Window(width=800, height=600)
        self.player1 = Player(xpos=self.window.width - 50, ypos=self.window.height/2)
        self.player2 = Player(50, ypos=self.window.height/2)

        await self.send_positions()

    async def disconnect(self, close_code):
        # Remove player from the dictionary when disconnected
        player_index = None
        for index, channel_name in self.players.items():
            if channel_name == self.channel_name:
                player_index = index
                break

        if player_index is not None:
            del self.players[player_index]

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        # Only allow the first connected client to control player1
        if message == 'move_up_player':
            if self.players[0] == self.channel_name:
                self.player1.move_up()
            elif self.players[1] == self.channel_name:
                self.player2.move_up()
        elif message == 'move_down_player':
            if self.players[0] == self.channel_name:
                self.player1.move_down()
            elif self.players[1] == self.channel_name:
                self.player2.move_down()
        # Send updated player and ball positions to all connected clients
        await self.send_positions()

    async def send_positions(self):
        # Broadcast updated positions to all connected clients
        await self.send(text_data=json.dumps({
            'player1': self.player1.to_dict(),
            'player2': self.player2.to_dict()
        }))
