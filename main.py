from random import randint

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty
)
from kivy.uix.widget import Widget
from kivy.vector import Vector

STEP_SIZE = 15
WINDOW_HEIGHT = 800
WINDOW_WIDTH = 800


def random_pos_on_grid():
    """
    :return: A random position on the map. It will be on a multiple of STEP_SIZE
    """
    return [
        randint(0, (int((WINDOW_WIDTH - STEP_SIZE) / STEP_SIZE))) * STEP_SIZE,
        randint(0, (int((WINDOW_HEIGHT - STEP_SIZE) / STEP_SIZE))) * STEP_SIZE]


class Body(Widget):
    """
    A cell of the snake body
    """
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        """
        Move a snake cell
        """
        self.pos = Vector(*self.velocity) + self.pos
        self._on_touch_wall()

    def _on_touch_wall(self):
        """
        Check if the snake cell touch a wall
        """
        if (self.y + STEP_SIZE > WINDOW_HEIGHT) or (self.y < 0):
            self.y = abs(abs(self.y) - WINDOW_HEIGHT)
        if (self.x < 0) or (self.x + STEP_SIZE > WINDOW_WIDTH):
            self.x = abs(abs(self.x) - WINDOW_WIDTH)


class Fruit(Widget):
    """
    the fruit
    """
    pass

class SnakeGame(Widget):
    """
    The snake game
    """
    snake = ObjectProperty(None)
    fruit = ObjectProperty(None)
    score = NumericProperty(0)

    def __init__(self, **kwargs):
        super(SnakeGame, self).__init__(**kwargs)
        Window.size = (WINDOW_WIDTH, WINDOW_HEIGHT)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def start(self, vel=(STEP_SIZE, 0)):
        """
        Start the game.
        :param vel: default velocity
        """
        self.snake.size = (STEP_SIZE, STEP_SIZE)
        self.snake.pos = random_pos_on_grid()
        self.snake.velocity = vel
        self.fruit.size = (STEP_SIZE, STEP_SIZE)
        self.spawn_fruit()

    def spawn_fruit(self):
        """
        Spawn a fruit on the map
        """
        self.fruit.pos = random_pos_on_grid()

    def _is_fruit_touched(self):
        """
        :return: true if the snake touch the fruit
        """
        return self.snake.x == self.fruit.x and self.snake.y == self.fruit.y

    def on_touch_fruit(self):
        """
        The snake get the point if it touch the fruit. The fruit respawn
        """
        if self._is_fruit_touched():
            self.score += 1
            self.spawn_fruit()
            print(self.score)

    def update(self, dt):
        """
        Move the snake and check if it touch the fruit
        """
        self.snake.move()
        self.on_touch_fruit()

    def _going_down(self):
        """
        Check if the snake is going down
        """
        return self.snake.velocity_x == 0 and self.snake.velocity_y == -STEP_SIZE

    def _going_up(self):
        """
        Check if the snake is going up
        """
        return self.snake.velocity_x == 0 and self.snake.velocity_y == STEP_SIZE

    def _going_left(self):
        """
        Check if the snake is going left
        """
        return self.snake.velocity_x == -STEP_SIZE and self.snake.velocity_y == 0

    def _going_right(self):
        """
        Check if the snake is going right
        """
        return self.snake.velocity_x == STEP_SIZE and self.snake.velocity_y == 0

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        """
            Check if there is an arrow input
        """
        if keycode[1] == 'up' and not self._going_down():
            self.snake.velocity = (0, STEP_SIZE)
        elif keycode[1] == 'down' and not self._going_up():
            self.snake.velocity = (0, -STEP_SIZE)
        elif keycode[1] == 'left' and not self._going_right():
            self.snake.velocity = (-STEP_SIZE, 0)
        elif keycode[1] == 'right' and not self._going_left():
            self.snake.velocity = (STEP_SIZE, 0)
        return True

    def _keyboard_closed(self):
        """
        Close the keyboard
        """
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None


class SnakeApp(App):
    def build(self):
        game = SnakeGame()
        game.start()
        Clock.schedule_interval(game.update, 5.0 / 60.0)
        return game


if __name__ == '__main__':
    SnakeApp().run()
