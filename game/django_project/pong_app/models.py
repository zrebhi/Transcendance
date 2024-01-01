# models.py
import asyncio
class Player:
    def __init__(self, xpos, ypos):
        self.xpos = xpos
        self.ypos = ypos
        self.width = 20
        self.height = 90
        self.step = 10

    def move_up(self):
        self.ypos -= self.step

    def move_down(self):
        self.ypos += self.step

    def to_dict(self):
        return {
            'xpos': self.xpos,
            'ypos': self.ypos,
            'width': self.width,
            'height': self.height
        }

    def collides_with(self, ball):
        # Check if any point on the ball's circumference is inside the player's rectangle

        # Check left side of ball
        left_collision = self.xpos <= (ball.xpos - ball.radius) <= (self.xpos + self.width) and \
                         self.ypos <= ball.ypos <= (self.ypos + self.height)

        # Check right side of ball
        right_collision = self.xpos <= (ball.xpos + ball.radius) <= (self.xpos + self.width) and \
                          self.ypos <= ball.ypos <= (self.ypos + self.height)

        # Check top side of ball
        top_collision = self.ypos <= (ball.ypos - ball.radius) <= (self.ypos + self.height) and \
                        self.xpos <= ball.xpos <= (self.xpos + self.width)

        # Check bottom side of ball
        bottom_collision = self.ypos <= (ball.ypos + ball.radius) <= (self.ypos + self.height) and \
                           self.xpos <= ball.xpos <= (self.xpos + self.width)

        # Return True if there's a collision on any side
        return left_collision or right_collision or top_collision or bottom_collision


# models.py

class Ball:
    def __init__(self, xpos, ypos):
        self.xpos = xpos
        self.ypos = ypos
        self.radius = 10
        self.velocity = 2
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
        self.players = {}
        self.player1 = Player(50, ypos=self.window.height / 2)
        self.player2 = Player(xpos=self.window.width - 50, ypos=self.window.height / 2)
        self.ball = Ball(xpos=self.window.width / 2, ypos=self.window.height / 2)
        self.pause_game = 1

    def move_player(self, player, direction):
        if player == 1:
            if direction == 'up':
                self.player1.move_up()
            elif direction == 'down':
                self.player1.move_down()
        elif player == 2:
            if direction == 'up':
                self.player2.move_up()
            elif direction == 'down':
                self.player2.move_down()

    def loop(self):
        if not self.pause_game:
            self.ball.move()
            self.check_collisions()

    def check_collisions(self):
        if self.player1.collides_with(self.ball) or self.player2.collides_with(self.ball):
            self.ball.reflect_horizontal()

        if self.ball.ypos - self.ball.radius <= 0 or self.ball.ypos + self.ball.radius >= self.window.height:
            self.ball.reflect_vertical()

        if self.ball.xpos - self.ball.radius <= 0 or self.ball.xpos + self.ball.radius >= self.window.width:
            self.ball.xpos = self.window.width / 2
            self.ball.ypos = self.window.height / 2
            self.ball.x_speed = -self.ball.x_speed

    def get_state(self):
        return {
            'window': self.window.to_dict(),
            'player1': self.player1.to_dict(),
            'player2': self.player2.to_dict(),
            'ball': self.ball.to_dict(),
        }
