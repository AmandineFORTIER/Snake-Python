from random import randint

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty
)
from kivy.uix.widget import Widget
from kivy.vector import Vector

STEP_SIZE = 20
WINDOW_HEIGHT = 600
WINDOW_WIDTH = 600


def random_pos_on_grid():
    """
    :return: A random position on the map. It will be on a multiple of STEP_SIZE
    """
    return [
        randint(0, (int((WINDOW_WIDTH - STEP_SIZE) / STEP_SIZE))) * STEP_SIZE,
        randint(0, (int((WINDOW_HEIGHT - STEP_SIZE) / STEP_SIZE))) * STEP_SIZE]


class SnakeTail(Widget):

    def move(self, new_pos):
        self.pos = new_pos


class SnakeHead(Widget):
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
        if (self.y < 0) or (self.y + STEP_SIZE > WINDOW_HEIGHT):
            self.y = (int(WINDOW_HEIGHT / STEP_SIZE) * STEP_SIZE) - STEP_SIZE if (self.y < 0) else 0
        if (self.x < 0) or (self.x + STEP_SIZE > WINDOW_WIDTH):
            self.x = (int(WINDOW_WIDTH / STEP_SIZE) * STEP_SIZE) - STEP_SIZE if (self.x < 0) else 0


class Fruit(Widget):
    """
    the fruit
    """
    x = NumericProperty(0)
    y = NumericProperty(0)
    pos = ReferenceListProperty(x, y)

    def spawn(self):
        """
        Spawn a fruit on the map
        """
        self.pos = random_pos_on_grid()


class SnakeGame(Widget):
    """
    The snake game
    """
    snake_head = ObjectProperty(None)
    fruit = ObjectProperty(None)
    score = NumericProperty(0)
    player_size = NumericProperty(STEP_SIZE)

    def __init__(self, **kwargs):
        super(SnakeGame, self).__init__(**kwargs)
        Window.size = (WINDOW_WIDTH, WINDOW_HEIGHT)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self.tail = []

    def start(self, vel=(STEP_SIZE, 0)):
        """
        Start the game.
        :param vel: default velocity
        """
        self.snake_head.pos = random_pos_on_grid()
        self.snake_head.velocity = vel
        self.tail.append(
            SnakeTail(
                pos=(self.snake_head.pos[0] - STEP_SIZE, self.snake_head.pos[1]),
                size=self.snake_head.size
            )
        )
        self.add_widget(self.tail[-1])

        self.tail.append(
            SnakeTail(
                pos=(self.snake_head.pos[0] - 2 * STEP_SIZE, self.snake_head.pos[1]),
                size=self.snake_head.size
            )
        )
        self.add_widget(self.tail[-1])
        self.fruit.spawn()

    def _is_fruit_touched(self):
        """
        :return: true if the snake touch the fruit
        """
        return self.snake_head.x == self.fruit.x and self.snake_head.y == self.fruit.y

    def on_touch_fruit(self):
        """
        The snake get the point if it touch the fruit. The fruit respawn
        """
        if self._is_fruit_touched():
            self.score += 1
            self.fruit.spawn()
            self.tail.append(
                SnakeTail(
                    pos=self.tail[-1].pos,
                    size=self.snake_head.size
                )
            )
            self.add_widget(self.tail[-1])

    def update(self, dt):
        """
        Move the snake and check if it touch the fruit
        """
        for i in range(1, len(self.tail)):
            self.tail[-i].move(new_pos=(self.tail[-(i + 1)].pos))
        self.tail[0].move(new_pos=self.snake_head.pos)
        self.snake_head.move()
        self.on_touch_fruit()

    def _going_down(self):
        """
        Check if the snake is going down
        """
        return self.snake_head.velocity_x == 0 and self.snake_head.velocity_y == -STEP_SIZE

    def _going_up(self):
        """
        Check if the snake is going up
        """
        return self.snake_head.velocity_x == 0 and self.snake_head.velocity_y == STEP_SIZE

    def _going_left(self):
        """
        Check if the snake is going left
        """
        return self.snake_head.velocity_x == -STEP_SIZE and self.snake_head.velocity_y == 0

    def _going_right(self):
        """
        Check if the snake is going right
        """
        return self.snake_head.velocity_x == STEP_SIZE and self.snake_head.velocity_y == 0

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        """
            Check if there is an arrow input
        """
        if keycode[1] == 'up' and not self._going_down():
            self.snake_head.velocity = (0, STEP_SIZE)
        elif keycode[1] == 'down' and not self._going_up():
            self.snake_head.velocity = (0, -STEP_SIZE)
        elif keycode[1] == 'left' and not self._going_right():
            self.snake_head.velocity = (-STEP_SIZE, 0)
        elif keycode[1] == 'right' and not self._going_left():
            self.snake_head.velocity = (STEP_SIZE, 0)
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
