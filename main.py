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
    """
    Tail of the snake
    """

    def move(self, new_pos):
        """
        Move the snake tail
        :param new_pos: New pos of the tail
        """
        self.pos = new_pos


class SnakeHead(Widget):
    """
    The snake head
    """
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        """
        Move the snake head
        """
        self.pos = Vector(*self.velocity) + self.pos
        self._on_touch_wall()

    def _on_touch_wall(self):
        """
        Check if the snake head touch a wall
        """
        if (self.y < 0) or (self.y + STEP_SIZE > WINDOW_HEIGHT):
            self.y = (int(WINDOW_HEIGHT / STEP_SIZE) * STEP_SIZE) - STEP_SIZE if (self.y < 0) else 0
        if (self.x < 0) or (self.x + STEP_SIZE > WINDOW_WIDTH):
            self.x = (int(WINDOW_WIDTH / STEP_SIZE) * STEP_SIZE) - STEP_SIZE if (self.x < 0) else 0

    def is_touching(self, pos):
        """
        Check if snake head is touching a pos
        :param pos: The pos we want to check is snake head is touching it
        :return: True if snake head is touching it
        """
        return pos[0] <= self.pos[0] < pos[0] + STEP_SIZE and pos[1] <= self.pos[1] < pos[1] + STEP_SIZE


class Fruit(Widget):
    """
    The fruit
    """

    def move(self, pos):
        """
        Move a fruit to a new position
        :param pos: The new pos of the fruit
        """
        self.pos = pos


class SnakeGame(Widget):
    """
    The snake game
    """
    snake_head = ObjectProperty(None)
    fruit = ObjectProperty(None)
    score = NumericProperty(0)
    player_size = NumericProperty(STEP_SIZE)
    tail = []

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
        self.snake_head.pos = random_pos_on_grid()
        self.snake_head.velocity = vel
        self.add_tail((self.snake_head.pos[0] - STEP_SIZE, self.snake_head.pos[1]))
        self.add_tail((self.snake_head.pos[0] - (2 * STEP_SIZE), self.snake_head.pos[1]))
        self.fruit.move(random_pos_on_grid())

    def add_tail(self, pos):
        self.tail.append(
            SnakeTail(
                pos=pos,
                size=self.snake_head.size
            )
        )
        self.add_widget(self.tail[-1])

    def update(self, dt):
        """
        Move the snake and check if it touch the fruit
        """
        for i in range(1, len(self.tail)):
            if self.snake_head.is_touching(self.tail[i].pos):
                print("TOUCH ",i)
            self.tail[-i].move(new_pos=self.tail[-(i + 1)].pos)
        self.tail[0].move(new_pos=self.snake_head.pos)
        self.snake_head.move()
        self.on_touch_fruit()

    def on_touch_fruit(self):
        """
        The snake get the point if it touch the fruit. The fruit respawn and the snake tail growth.
        """
        if self.snake_head.is_touching(self.fruit.pos):
            self.score += 1
            self.fruit.move(random_pos_on_grid())
            self.add_tail(self.tail[-1].pos)

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
        Clock.schedule_interval(game.update, 20.0 / 60.0)
        return game


if __name__ == '__main__':
    SnakeApp().run()
