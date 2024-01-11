import asyncio

from django.db import models

WINNING_SCORE = 3
PLAYER_WIDTH, PLAYER_HEIGHT = 20, 100
BALL_RADIUS = 10
BALL_SPEED = 10
PLAYER_SPEED = 6
BALL_RESET_COOLDOWN = 1500

#Paddle class
class Player:
	#Movement speed of the paddle
	def __init__(self, x, y):
		self.xpos = x
		self.ypos = y
		self.width = PLAYER_WIDTH
		self.height = PLAYER_HEIGHT
		self.vel = PLAYER_SPEED
		self.score = 0

	def move_up(self):
		if self.ypos - self.height//2 >= 0:
			self.ypos -= self.vel

	def move_down(self, window):
		if self.ypos + self.height//2 <= window.height:
			self.ypos += self.vel

	def reset(self):
		self.ypos = window.height//2

	def add_score(self):
		self.score += 1

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

#Ball class
class Ball:
	def __init__(self, x, y):
		self.xpos = self.original_x = x
		self.ypos = self.original_y = y
		self.radius = BALL_RADIUS
		self.max_vel = BALL_SPEED
		self.x_vel = self.max_vel
		self.y_vel = 0

	def move(self):
		self.xpos += self.x_vel
		self.ypos += self.y_vel

	def reset(self):
		self.direction = (self.x_vel * -1)
		self.xpos = self.original_x
		self.ypos = self.original_y
		self.y_vel = 0
		self.x_vel = self.direction
		self.direction = 0

	def reflect_vertical(self):
		self.y_vel = -self.y_vel

	#Handling ball collision
	def handle_ball_collision(self, player):
		self.x_vel *= -1
		difference_in_y = player.ypos - self.ypos
		reduction_factor = (player.height / 2) / self.max_vel
		y_vel = difference_in_y / reduction_factor
		self.y_vel = -1 * y_vel

	def to_dict(self):
		return {
			'xpos': self.xpos,
			'ypos': self.ypos,
			'x_speed': self.x_vel,
			'y_speed': self.y_vel,
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
		self.player1 = Player(50, self.window.height / 2)
		self.player2 = Player(self.window.width - 50, self.window.height / 2)
		self.ball = Ball(self.window.width / 2, self.window.height / 2)
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
			self.ball.handle_ball_collision(self.player1)
			self.ball.xpos = self.player1.xpos + self.player1.width + self.ball.radius

		if self.player2.collides_with(self.ball):
			self.ball.handle_ball_collision(self.player2)
			self.ball.xpos = self.player2.xpos - self.ball.radius

		if self.ball.ypos - self.ball.radius <= 0 or self.ball.ypos + self.ball.radius >= self.window.height:
			self.ball.reflect_vertical()

		if self.ball.xpos - self.ball.radius <= 0 or self.ball.xpos + self.ball.radius >= self.window.width:
			self.handle_score()
			self.ball.reset()

	def handle_score(self):
		if self.ball.xpos - self.ball.radius <= 0:
			self.player2.add_score()
		if self.ball.xpos + self.ball.radius >= self.window.width:
			self.player1.add_score()
		if self.player1.score == WINNING_SCORE or self.player2.score == WINNING_SCORE:
			if self.player1.score == WINNING_SCORE:
				print("Player 1 won !")
			else:
				print("Player 2 won !")
			self.running = False
			self.pause_game = True

	def get_state(self):
		return {
			'window': self.window.to_dict(),
			'player1': self.player1.to_dict(),
			'player2': self.player2.to_dict(),
			'ball': self.ball.to_dict(),
			'pause': self.pause_game
		}