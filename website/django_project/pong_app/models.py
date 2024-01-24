import asyncio
import time


class Paddle:
    """Represents a paddle in the game with position, size, movement capabilities, and score."""

    def __init__(self, xpos, ypos):
        self.xpos = xpos
        self.ypos = ypos
        self.width = 20
        self.height = 90
        self.step = 15
        self.score = 0
        self.player_name = None
        self.pause_timer = 120
        self.pause_request = False
        self.connected = False

    def move_up(self):
        """Move the paddle up within window boundaries."""
        if self.ypos - self.step >= -self.height / 2:
            self.ypos -= self.step

    def move_down(self, window):
        """Move the paddle down within window boundaries."""
        if self.ypos + self.step <= window.height - self.height / 2:
            self.ypos += self.step

    def collides_with(self, ball):
        """Check if the paddle collides with the ball."""
        return (self.xpos < ball.xpos + ball.radius and
                self.xpos + self.width > ball.xpos - ball.radius and
                self.ypos < ball.ypos + ball.radius and
                self.ypos + self.height > ball.ypos - ball.radius)

    def to_dict(self):
        """Convert paddle's state to a dictionary for serialization."""
        return {
            'xpos': self.xpos,
            'ypos': self.ypos,
            'width': self.width,
            'height': self.height,
            'score': self.score,
            'pause_request': self.pause_request,
            'pause_timer': self.pause_timer,
            'connected': self.connected,
        }


class Ball:
    """Represents the ball in the game with position, size, and velocity."""

    def __init__(self, xpos, ypos):
        self.xpos = xpos
        self.ypos = ypos
        self.radius = 10
        self.velocity = 8
        self.x_speed = self.velocity
        self.y_speed = self.velocity

    def move(self):
        """Move the ball based on its current velocity."""
        self.xpos += self.x_speed
        self.ypos += self.y_speed

    def reflect_horizontal(self, player_number, player):
        """Reflect the ball horizontally on paddle collision and adjust trajectory."""
        self.x_speed = -self.x_speed
        hit_pos = (self.ypos - player.ypos) / player.height
        self.y_speed += hit_pos * self.velocity
        if player_number == 1:
            self.xpos = player.xpos + player.width + self.radius
        elif player_number == 2:
            self.xpos = player.xpos - player.width - self.radius

    def reflect_vertical(self):
        """Reflect the ball vertically on wall collision."""
        self.y_speed = -self.y_speed

    def to_dict(self):
        """Convert ball's state to a dictionary for serialization."""
        return {
            'xpos': self.xpos,
            'ypos': self.ypos,
            'x_speed': self.x_speed,
            'y_speed': self.y_speed,
            'radius': self.radius,
        }


class Window:
    """Represents the game window with dimensions."""

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def to_dict(self):
        """Convert window's dimensions to a dictionary for serialization."""
        return {
            'width': self.width,
            'height': self.height
        }


class Game:
    """Main game class managing the state and logic of the Pong game."""

    def __init__(self, winning_score=10):
        self.session = None
        self.window = Window(width=1200, height=900)
        self.players = [None, None]
        self.paddle1 = Paddle(50, ypos=self.window.height / 2)
        self.paddle2 = Paddle(self.window.width - 50, ypos=self.window.height / 2)
        self.ball = Ball(xpos=self.window.width / 2, ypos=self.window.height / 2)
        self.move_commands = []
        self.status = 'initializing'
        self.winning_score = winning_score
        self.winner = None

    async def ball_loop(self):
        """Game loop to process ball movements."""
        if self.status == 'ongoing':
            self.ball.move()
            self.check_collisions()

    async def paddles_loop(self):
        """Game loop to process player movements."""
        while self.move_commands:
            player_number, direction = self.move_commands.pop(0)
            self.move_player(player_number, direction)

    def move_player(self, player_number, direction):
        """Move the specified player in the given direction."""
        paddle = self.paddle1 if player_number == 1 else self.paddle2
        if direction == 'up':
            paddle.move_up()
        elif direction == 'down':
            paddle.move_down(self.window)

    def check_collisions(self):
        """Check for and handle collisions in the game."""
        if self.paddle1.collides_with(self.ball):
            self.handle_paddle_collision(self.paddle1, 1)
        elif self.paddle2.collides_with(self.ball):
            self.handle_paddle_collision(self.paddle2, 2)
        if self.ball.ypos - self.ball.radius <= 0 or self.ball.ypos + self.ball.radius >= self.window.height:
            self.ball.reflect_vertical()
        self.check_ball_out_of_bounds()

    def handle_paddle_collision(self, paddle, player_number):
        """Handle ball collision with the specified paddle."""
        if (self.ball.ypos + self.ball.radius < paddle.ypos or
                self.ball.ypos - self.ball.radius > paddle.ypos + paddle.height):
            self.ball.reflect_vertical()
        else:
            self.ball.reflect_horizontal(player_number, paddle)

    def check_ball_out_of_bounds(self):
        """Check if the ball is out of bounds and update scores."""
        if self.ball.xpos <= 0 or self.ball.xpos >= self.window.width:
            scoring_paddle = self.paddle2 if self.ball.xpos <= 0 else self.paddle1
            scoring_paddle.score += 1
            self.reset_ball()
            self.check_win_condition()

    def check_win_condition(self):
        """Check if a player has reached the winning score."""
        if self.paddle1.score == self.winning_score:
            self.winner = self.paddle1.player_name
        elif self.paddle2.score == self.winning_score:
            self.winner = self.paddle2.player_name
        if self.winner:
            self.status = 'finished'

    def reset_ball(self):
        """Reset the ball to the center with a delay."""
        self.ball.xpos = self.window.width / 2
        self.ball.ypos = self.window.height / 2
        self.ball.x_speed = -self.ball.x_speed
        self.ball.y_speed = 0
        for paddle in [self.paddle1, self.paddle2]:
            if paddle.pause_request:
                self.status = 'paused'
                asyncio.create_task(self.pause_timer_tick(paddle))
        asyncio.create_task(self.delay_game_for(1))

    async def delay_game_for(self, seconds):
        """Introduce a delay in the game."""
        if self.status == 'ongoing':
            self.status = 'delayed'
        await asyncio.sleep(seconds)
        if self.status == 'delayed':
            self.status = 'ongoing'

    async def pause_timer_tick(self, paddle):
        """Decrement the pause timer."""
        while self.status == 'paused':
            if paddle.pause_timer <= 0:
                paddle.pause_request = False
                self.resume_game()
                break
            paddle.pause_timer -= 1
            await asyncio.sleep(1)

    def pause_request(self, player_number):
        """Handle a player's pause request."""
        paddle = self.paddle1 if player_number == 1 else self.paddle2
        if paddle.pause_timer >= 0:
            paddle.pause_request = True

    def resume_game(self):
        """Resume the game."""
        if not self.paddle1.pause_request and not self.paddle2.pause_request:
            self.status = 'ongoing'
            asyncio.create_task(self.delay_game_for(3))

    def get_state(self):
        """Get the current state of the game for broadcasting."""
        return {
            'paddle1': self.paddle1.to_dict(),
            'paddle2': self.paddle2.to_dict(),
            'ball': self.ball.to_dict(),
            'status': self.status,
        }

    def get_initial_data(self, local_game):
        """Get initial game data for WebSocket communication."""
        mode = "Local" if local_game else "Online"
        return {
            'window': self.window.to_dict(),
            'mode': mode,
            'player1': self.paddle1.player_name,
            'player2': self.paddle2.player_name,
            **self.get_state()
        }
