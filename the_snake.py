from random import randint

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Координаты центра экрана:
CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Новое направление в зависимости от текущего направления и нажатой клавиши:
DIRECTIONS = {
    (LEFT, pg.K_UP): UP,
    (RIGHT, pg.K_UP): UP,
    (UP, pg.K_UP): UP,
    (LEFT, pg.K_DOWN): DOWN,
    (RIGHT, pg.K_DOWN): DOWN,
    (DOWN, pg.K_DOWN): DOWN,
    (UP, pg.K_LEFT): LEFT,
    (DOWN, pg.K_LEFT): LEFT,
    (LEFT, pg.K_LEFT): LEFT,
    (UP, pg.K_RIGHT): RIGHT,
    (DOWN, pg.K_RIGHT): RIGHT,
    (RIGHT, pg.K_RIGHT): RIGHT,
}

# Цвета элементов игры:
BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки (ходов в секунду):
SPEED = 10

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(
        self,
        body_color=(0, 0, 0),
        position=CENTER,
    ):
        self.body_color = body_color
        self.position = position

    def draw_cell(self, position, color=None):
        """Отрисовывает одну ячейку игрового поля."""
        if color is None:
            color = self.body_color
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color, rect)
        # Для цвета фона рамку не рисуем — так ячейка полностью затирается.
        if color != BOARD_BACKGROUND_COLOR:
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self):
        """Отрисовка объекта. Переопределяется в дочерних классах."""
        raise NotImplementedError(
            'Метод draw() должен быть реализован в дочернем классе.'
        )


class Apple(GameObject):
    """Яблоко, которое собирает змейка."""

    def __init__(self, occupied_positions=None):
        super().__init__(APPLE_COLOR)
        if occupied_positions is None:
            occupied_positions = [self.position]
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions=()):
        """Размещает яблоко в случайной свободной ячейке игрового поля."""
        while self.position in occupied_positions:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )

    def draw(self):
        """Отрисовывает яблоко на игровом поле."""
        self.draw_cell(self.position)


class Snake(GameObject):
    """Змейка, которой управляет игрок."""

    def __init__(self):
        super().__init__(SNAKE_COLOR)
        self.reset()

    def reset(self):
        """Возвращает змейку в начальное состояние."""
        self.length = 1
        self.positions = [CENTER]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def update_direction(self):
        """Применяет направление, выбранное игроком."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Перемещает змейку на одну клетку в текущем направлении."""
        head_x, head_y = self.get_head_position()
        direction_x, direction_y = self.direction
        new_head = (
            (head_x + direction_x * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + direction_y * GRID_SIZE) % SCREEN_HEIGHT,
        )
        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def get_head_position(self):
        """Возвращает координаты головы змейки."""
        return self.positions[0]

    def draw(self):
        """Затирает последний сегмент и отрисовывает голову змейки."""
        # Затирание последнего сегмента.
        if self.last:
            self.draw_cell(self.last, BOARD_BACKGROUND_COLOR)

        # Отрисовка головы змейки.
        self.draw_cell(self.get_head_position())


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш и закрытие окна."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        if event.type == pg.KEYDOWN:
            new_direction = DIRECTIONS.get(
                (game_object.direction, event.key)
            )
            if new_direction is not None:
                game_object.next_direction = new_direction


def main():
    """Запускает игру «Змейка»."""
    # Инициализация PyGame:
    pg.init()

    snake = Snake()
    apple = Apple(snake.positions)

    # Экран очищается один раз перед началом игры.
    screen.fill(BOARD_BACKGROUND_COLOR)
    snake.draw()
    apple.draw()
    pg.display.update()

    while True:
        clock.tick(SPEED)

        handle_keys(snake)
        snake.update_direction()
        snake.move()

        # Если змейка съела яблоко — увеличиваем длину и создаём новое яблоко.
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)

        # Если змейка врезалась в себя — начинаем игру заново.
        elif snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            apple.randomize_position(snake.positions)
            # При рестарте очищаем экран целиком.
            screen.fill(BOARD_BACKGROUND_COLOR)

        snake.draw()
        apple.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
