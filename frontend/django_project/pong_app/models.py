# models.py
import asyncio

from django.db import models


class Player:
    def __init__(self, xpos, ypos):
        self.xpos = xpos
        self.ypos = ypos
        self.width = 20
        self.height = 90
        self.step = 10

    def move_up(self):
        # Ensure the player doesn't move up past the top boundary, keeping half inside
        if self.ypos - self.step >= -self.height / 2:
            self.ypos -= self.step

    def move_down(self, window):
        # Ensure the player doesn't move down past the bottom boundary, keeping half inside
        if self.ypos + self.step <= window.height - self.height / 2:
            self.ypos += self.step

    def collides_with(self, ball):
        # Simplified collision check with AABB (Axis-Aligned Bounding Box)
        return (self.xpos < ball.xpos + ball.radius and
                self.xpos + self.width > ball.xpos - ball.radius and
                self.ypos < ball.ypos + ball.radius and
                self.ypos + self.height > ball.ypos - ball.radius)

    def to_dict(self):
        return {
            'xpos': self.xpos,
            'ypos': self.ypos,
            'width': self.width,
            'height': self.height
        }

# models.py

class Ball:
    def __init__(self, xpos, ypos):
        self.xpos = xpos
        self.ypos = ypos
        self.radius = 10
        self.velocity = 10
        self.x_speed = self.velocity  # Adjust the speed as needed
        self.y_speed = self.velocity # Adjust the speed as needed

    def move(self):
        # Move the ball based on its current direction and speed
        self.xpos += self.x_speed
        self.ypos += self.y_speed

    def reflect_horizontal(self):
        # Reflect the ball horizontally (change its direction)
        self.x_speed = -self.x_speed

    def reflect_vertical(self):
        # Reflect the ball vertically (change its direction)
        self.y_speed = -self.y_speed

    def to_dict(self):
        return {
            'xpos': self.xpos,
            'ypos': self.ypos,
            'x_speed': self.x_speed,
            'y_speed': self.y_speed,
            'radius': self.radius,
        }


class Window:
    def __init__(self, width, height):
        self.width, self.height = width, height

    def to_dict(self):
        return {
            'width': self.width,
            'height': self.height
        }


class Game:
    def __init__(self, window):
        self.window = window
        self.reset_game()
        print('Game initialized')

    def reset_game(self):
        self.players = {0: None, 1: None}
        self.player1 = Player(50, ypos=self.window.height / 2)
        self.player2 = Player(xpos=self.window.width - 50, ypos=self.window.height / 2)
        self.ball = Ball(xpos=self.window.width / 2, ypos=self.window.height / 2)
        self.pause_game = True
        self.running = False

    def loop(self):
        if not self.pause_game:
            self.ball.move()
            self.check_collisions()

    def move_player(self, player, direction):
        if player == 1:
            if direction == 'up':
                self.player1.move_up()
            elif direction == 'down':
                self.player1.move_down(self.window)
        elif player == 2:
            if direction == 'up':
                self.player2.move_up()
            elif direction == 'down':
                self.player2.move_down(self.window)

    def check_collisions(self):
        # Player and ball collision
        if self.player1.collides_with(self.ball):
            self.ball.reflect_horizontal()
            # Reposition the ball outside the player's boundary
            self.ball.xpos = self.player1.xpos + self.player1.width + self.ball.radius

        if self.player2.collides_with(self.ball):
            self.ball.reflect_horizontal()
            # Reposition the ball outside the player's boundary
            self.ball.xpos = self.player2.xpos - self.ball.radius

        # Wall collision
        if self.ball.ypos - self.ball.radius <= 0 or self.ball.ypos + self.ball.radius >= self.window.height:
            self.ball.reflect_vertical()

        # Out of bounds check
        if self.ball.xpos - self.ball.radius <= 0 or self.ball.xpos + self.ball.radius >= self.window.width:
            self.reset_ball()

    def reset_ball(self):
        self.ball.xpos = self.window.width / 2
        self.ball.ypos = self.window.height / 2
        self.ball.x_speed = -self.ball.x_speed

    def get_state(self):
        return {
            'window': self.window.to_dict(),
            'player1': self.player1.to_dict(),
            'player2': self.player2.to_dict(),
            'ball': self.ball.to_dict(),
            'pause': self.pause_game
        }
