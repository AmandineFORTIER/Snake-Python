from random import randint

from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty, BooleanProperty, StringProperty
)
from kivy.uix.widget import Widget
from kivy.vector import Vector

STEP_SIZE = 20
WINDOW_HEIGHT = 600
WINDOW_WIDTH = 600


def random_pos_on_grid(step_size, width, height):
    """
    Give a random position on the window and at a multiple of step_size
    :param step_size: The step size
    :param width: Window width
    :param height: Windows height
    :return: A random position on the map. It will be on a multiple of step_size
    """
    return [
        randint(0, (int((width - step_size) / step_size))) * step_size,
        randint(0, (int((height - step_size) / step_size))) * step_size]


class SnakeCell(Widget):
    """
    A snake cell
    """
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        """
        Move the snake cell
        """
        self.pos = Vector(*self.velocity) + self.pos

    def move_pos(self, pos):
        """
        Move the snake cell at a new position
        """
        self.pos = pos

    def go_to(self, direction, step_size):
        """
        Modify the object direction
        :param step_size: Step size of a cell
        :param direction: right, left, up, down or stop to move the object at this direction
        """
        if direction == "right":
            self.velocity = (step_size, 0)
        elif direction == "left":
            self.velocity = (-step_size, 0)
        elif direction == "up":
            self.velocity = (0, step_size)
        elif direction == "down":
            self.velocity = (0, -step_size)
        elif direction == "stop":
            self.velocity = (0, 0)


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
    tail = []
    position_to_go = StringProperty("right")
    is_game_over = BooleanProperty(False)

    def __init__(self, step_size, width, height, **kwargs):
        """
        Initialise the game
        :param step_size: Size of the step of a snake
        :param width: Window's width
        :param height: Window's height
        :param kwargs:
        """
        super(SnakeGame, self).__init__(**kwargs)
        Window.size = (width, height)
        self.step_size = step_size
        self._init_keyboard()
        self._set_objects_size()

    def _init_keyboard(self):
        """
        Initialise the keyboard
        """
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        """
            Check if there is an arrow input
        """
        if ((keycode[1] == 'up' and not self._is_going_to("down"))
                or (keycode[1] == 'down' and not self._is_going_to("up"))
                or (keycode[1] == 'left' and not self._is_going_to("right"))
                or (keycode[1] == 'right' and not self._is_going_to("left"))):
            self.position_to_go = keycode[1]
            return True
        return False

    def _keyboard_closed(self):
        """
        Close the keyboard
        """
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _set_objects_size(self):
        """
        Set the object size
        """
        self.snake_head.size = (self.step_size, self.step_size)
        self.fruit.size = self.snake_head.size

    def start(self):
        """
        Start the game.
        """
        self._add_objects_on_grid()
        self._add_cells_to_tail()

    def _add_objects_on_grid(self):
        """
        Add snake head and fruit on the grid
        """
        self.snake_head.pos = random_pos_on_grid(self.step_size, Window.width, Window.height)
        self.fruit.move(random_pos_on_grid(self.step_size, Window.width, Window.height))

    def _add_cells_to_tail(self):
        """
        Add 2 cells to the tail.
        :return:
        """
        self._growth_tail((self.snake_head.pos[0] - self.step_size, self.snake_head.pos[1]))
        self._growth_tail((self.snake_head.pos[0] - (2 * self.step_size), self.snake_head.pos[1]))

    def _growth_tail(self, pos):
        """
        Growth the snake's tail
        :param pos: The position where we want to add the new cell snake
        """
        self.tail.append(
            SnakeCell(
                pos=pos,
                size=self.snake_head.size
            )
        )
        self.add_widget(self.tail[-1])

    def update(self, dt):
        """
        Move the snake and check if it touch the fruit or if it's the end of the game
        """
        if not self.is_game_over:
            self.snake_head.go_to(self.position_to_go, self.step_size)
            self._on_touch_wall()
            self._move_snake()
            if not self.is_game_over:
                if self._snake_head_is_touching(self.fruit):
                    self._on_touch_fruit()

    def _on_touch_wall(self):
        """
        Check if the snake head touch a wall
        """
        if (self.snake_head.y < 0) or (self.snake_head.y + self.step_size > Window.height):
            self.snake_head.y = (int(Window.height / self.step_size) * self.step_size) - self.step_size \
                if (self.snake_head.y < 0) else 0
        if (self.snake_head.x < 0) or (self.snake_head.x + self.step_size > Window.width):
            self.snake_head.x = (int(Window.width / self.step_size) * self.step_size) - self.step_size \
                if (self.snake_head.x < 0) else 0

    def _move_snake(self):
        for i in range(1, len(self.tail)):
            if self._snake_head_is_touching(self.tail[i]):
                self.game_over()
            self.tail[-i].move_pos(self.tail[-(i + 1)].pos)
        self.tail[0].move_pos(self.snake_head.pos)
        self.snake_head.move()

    def _snake_head_is_touching(self, obj):
        """
        Check if snake head is touching an object
        :param obj: the object we want to check is snake head is touching it
        :return: True if snake head is touching it
        """
        return obj.pos[0] <= self.snake_head.pos[0] < obj.pos[0] + self.step_size and \
               obj.pos[1] <= self.snake_head.pos[1] < obj.pos[1] + self.step_size

    def _on_touch_fruit(self):
        """
        The snake get the point. The fruit respawn and the snake tail growth.
        """
        self.score += 1
        self.fruit.move(random_pos_on_grid(self.step_size, Window.width, Window.height))
        self._growth_tail(self.tail[-1].pos)

    def game_over(self):
        self.snake_head.go_to("stop", self.step_size)
        for cell in self.tail:
            cell.go_to("stop", self.step_size)
        self._flash_screen(0.5)
        self.is_game_over = True

    def _flash_screen(self, time):
        """
        Flash the window
        """
        anim = Animation(opacity=0, duration=time)
        anim += Animation(opacity=1, duration=time)
        anim.repeat = True
        anim.start(self)

    def _is_going_to(self, direction):
        """
        check if the snake is going to a specific direction
        :param direction: right, left, up or down
        :return: true if the snake is going to this direction otherwise else
        """
        if direction == "right":
            return self.snake_head.velocity_x == self.step_size and self.snake_head.velocity_y == 0
        if direction == "left":
            return self.snake_head.velocity_x == -self.step_size and self.snake_head.velocity_y == 0
        if direction == "up":
            return self.snake_head.velocity_x == 0 and self.snake_head.velocity_y == self.step_size
        if direction == "down":
            return self.snake_head.velocity_x == 0 and self.snake_head.velocity_y == -self.step_size


class SnakeApp(App):
    def build(self):
        game = SnakeGame(STEP_SIZE, WINDOW_WIDTH, WINDOW_HEIGHT)
        game.start()
        Clock.schedule_interval(game.update, 10.0 / 60.0)
        return game


if __name__ == '__main__':
    SnakeApp().run()
