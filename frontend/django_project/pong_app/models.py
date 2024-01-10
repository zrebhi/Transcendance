import asyncio

class Player:
    """Represents a player in the game with position, size, and movement capabilities."""

    def __init__(self, xpos, ypos):
        self.xpos = xpos
        self.ypos = ypos
        self.width = 20
        self.height = 90
        self.step = 10

    def move_up(self):
        """Move the player up, ensuring they don't go past the top boundary."""
        if self.ypos - self.step >= -self.height / 2:
            self.ypos -= self.step

    def move_down(self, window):
        """Move the player down, ensuring they don't go past the bottom boundary."""
        if self.ypos + self.step <= window.height - self.height / 2:
            self.ypos += self.step

    def collides_with(self, ball):
        """Check for collision with the ball using Axis-Aligned Bounding Box (AABB)."""
        return (self.xpos < ball.xpos + ball.radius and
                self.xpos + self.width > ball.xpos - ball.radius and
                self.ypos < ball.ypos + ball.radius and
                self.ypos + self.height > ball.ypos - ball.radius)

    def to_dict(self):
        """Convert the player's state to a dictionary for easy serialization."""
        return {
            'xpos': self.xpos,
            'ypos': self.ypos,
            'width': self.width,
            'height': self.height
        }

class Ball:
    """Represents the ball in the game with position, size, and movement capabilities."""

    def __init__(self, xpos, ypos):
        self.xpos = xpos
        self.ypos = ypos
        self.radius = 10
        self.velocity = 8
        self.x_speed = self.velocity  # Horizontal speed
        self.y_speed = self.velocity  # Vertical speed

    def move(self):
        """Move the ball based on its current speed and direction."""
        self.xpos += self.x_speed
        self.ypos += self.y_speed

    def reflect_horizontal(self, player_number, player):
        """Reflect the ball's movement horizontally and reposition to avoid getting stuck."""
        self.x_speed = -self.x_speed

        # Reposition the ball outside the player's boundary
        if player_number == 1:
            self.xpos = player.xpos + player.width + self.radius
        elif player_number == 2:
            self.xpos = player.xpos - player.width - self.radius

    def reflect_vertical(self):
        """Reflect the ball's movement vertically (change y-direction)."""
        self.y_speed = -self.y_speed

    def to_dict(self):
        """Convert the ball's state to a dictionary for easy serialization."""
        return {
            'xpos': self.xpos,
            'ypos': self.ypos,
            'x_speed': self.x_speed,
            'y_speed': self.y_speed,
            'radius': self.radius,
        }

# ... Player and Game classes remain unchanged ...


class Window:
    """Represents the game window with its dimensions."""

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def to_dict(self):
        """Convert the window's dimensions to a dictionary for easy serialization."""
        return {
            'width': self.width,
            'height': self.height
        }

class Game:
    """Main game class managing the state and logic of the Pong game."""

    def __init__(self, window):
        self.window = window
        self.reset_game()
        asyncio.create_task(self.delay_game_for(0))

    def reset_game(self):
        """Initialize or reset the game to its starting state."""
        self.players = {0: None, 1: None}
        self.player1 = Player(50, ypos=self.window.height / 2)
        self.player2 = Player(xpos=self.window.width - 50, ypos=self.window.height / 2)
        self.ball = Ball(xpos=self.window.width / 2, ypos=self.window.height / 2)
        self.pause_game = True
        self.delay = False
        self.running = False

    def loop(self):
        """Main game loop that updates the game state if the game is running and not paused."""
        if not self.pause_game and not self.delay:
            self.ball.move()
            self.check_collisions()

    def move_player(self, player, direction):
        """Handle player movement based on the player number and direction."""
        player_obj = self.player1 if player == 1 else self.player2
        if direction == 'up':
            player_obj.move_up()
        elif direction == 'down':
            player_obj.move_down(self.window)

    def check_collisions(self):
        """Check and handle collisions between the ball and other game objects."""

        # Check collisions with players
        if self.player1.collides_with(self.ball):
            self.ball.reflect_horizontal(1, self.player1)
        elif self.player2.collides_with(self.ball):
            self.ball.reflect_horizontal(2, self.player2)

        # Check collisions with walls
        if self.ball.ypos - self.ball.radius <= 0 or self.ball.ypos + self.ball.radius >= self.window.height:
            self.ball.reflect_vertical()

        # Check if the ball is out of bounds
        if self.ball.xpos <= 0 or self.ball.xpos >= self.window.width:
            self.reset_ball()

    def reset_ball(self):
        """Reset the ball to the center and introduce a delay."""
        self.ball.xpos = self.window.width / 2
        self.ball.ypos = self.window.height / 2
        self.ball.x_speed = -self.ball.x_speed
        asyncio.create_task(self.delay_game_for(1))

    async def delay_game_for(self, seconds):
        """Delay the game for a specified number of seconds."""
        self.delay = True
        print(f'Game delayed for {seconds} seconds')
        await asyncio.sleep(seconds)
        self.delay = False

    def get_state(self):
        """Get the current state of the game for broadcasting to clients."""
        return {

            'player1': self.player1.to_dict(),
            'player2': self.player2.to_dict(),
            'ball': self.ball.to_dict(),
            'pause': self.pause_game
        }
