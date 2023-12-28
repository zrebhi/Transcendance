class Player:
    def __init__(self, xpos, ypos):
        self.xpos = xpos
        self.ypos = ypos
        self.width = 20
        self.height = 60
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
    def __init__(self, xpos, ypos, radius):
        self.xpos = xpos
        self.ypos = ypos
        self.radius = radius
        self.x_speed = 5  # Adjust the speed as needed
        self.y_speed = 5  # Adjust the speed as needed

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
        }


class Window:
    def __init__(self, width, height):
        self.width, self.height = width, height
