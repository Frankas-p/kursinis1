import random
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Tuple

import pygame

Position = Tuple[int, int]


class Config:
    WINDOW_WIDTH = 600
    WINDOW_HEIGHT = 600
    CELL_SIZE = 20
    GRID_WIDTH = WINDOW_WIDTH // CELL_SIZE
    GRID_HEIGHT = WINDOW_HEIGHT // CELL_SIZE
    FPS = 8

    LIGHT_COLOR = (50, 50, 50)
    DARK_COLOR = (30, 30, 30)

    START_BG_COLOR = (10, 10, 30)
    START_TITLE_COLOR = (0, 255, 0)
    START_TEXT_COLOR = (255, 255, 255)
    START_SUBTEXT_COLOR = (200, 200, 200)

    GAME_OVER_BG_COLOR = (40, 0, 0)

    SNAKE_COLOR = (0, 200, 0)
    SNAKE_HEAD_COLOR = (0, 141, 0)

    FOOD_COLOR = (220, 40, 40)
    FOOD_HIGHLIGHT_COLOR = (255, 120, 120)

    TEXT_COLOR = (255, 255, 0)
    GAME_OVER_COLOR = (141, 0, 0)

    HIGH_SCORE_FILE = Path("highscore.txt")


class HighScoreManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(HighScoreManager, cls).__new__(cls)
            cls._instance._high_score = 0
            cls._instance._load_high_score()
        return cls._instance

    def _load_high_score(self) -> None:
        if Config.HIGH_SCORE_FILE.exists():
            try:
                text = Config.HIGH_SCORE_FILE.read_text(encoding="utf-8").strip()
                self._high_score = int(text) if text else 0
            except (ValueError, OSError):
                self._high_score = 0
        else:
            self._high_score = 0
            self.save_high_score()

    @property
    def high_score(self) -> int:
        return self._high_score

    def update_if_better(self, score: int) -> None:
        if score > self._high_score:
            self._high_score = score
            self.save_high_score()

    def save_high_score(self) -> None:
        Config.HIGH_SCORE_FILE.write_text(str(self._high_score), encoding="utf-8")


class GameObject(ABC):
    def __init__(self, position: Position) -> None:
        self._position = position

    @property
    def position(self) -> Position:
        return self._position

    @position.setter
    def position(self, new_position: Position) -> None:
        self._position = new_position

    @abstractmethod
    def draw(self, screen: pygame.Surface) -> None:
        pass


class Food(GameObject):
    def draw(self, screen: pygame.Surface) -> None:
        center = (
            self._position[0] * Config.CELL_SIZE + Config.CELL_SIZE // 2,
            self._position[1] * Config.CELL_SIZE + Config.CELL_SIZE // 2,
        )
        radius = Config.CELL_SIZE // 2 - 2

        pygame.draw.circle(screen, Config.FOOD_COLOR, center, radius)
        pygame.draw.circle(
            screen,
            Config.FOOD_HIGHLIGHT_COLOR,
            (center[0] - 3, center[1] - 3),
            radius // 3,
        )


class Snake(GameObject):
    def __init__(self, position: Position) -> None:
        super().__init__(position)
        self._body: List[Position] = [position]
        self._direction: Position = (1, 0)
        self._grow_pending = 0

    @property
    def body(self) -> List[Position]:
        return list(self._body)

    @property
    def head(self) -> Position:
        return self._body[0]

    @property
    def direction(self) -> Position:
        return self._direction

    def set_direction(self, new_direction: Position) -> None:
        opposite = (-self._direction[0], -self._direction[1])
        if new_direction != opposite:
            self._direction = new_direction

    def move(self) -> None:
        x, y = self.head
        dx, dy = self._direction
        new_head = (x + dx, y + dy)

        self._body.insert(0, new_head)

        if self._grow_pending > 0:
            self._grow_pending -= 1
        else:
            self._body.pop()

        self._position = self.head

    def grow(self) -> None:
        self._grow_pending += 1

    def collides_with_self(self) -> bool:
        return self.head in self._body[1:]

    def collides_with_wall(self) -> bool:
        x, y = self.head
        return not (0 <= x < Config.GRID_WIDTH and 0 <= y < Config.GRID_HEIGHT)

    def draw(self, screen: pygame.Surface) -> None:
        for index, segment in enumerate(self._body):
            rect = pygame.Rect(
                segment[0] * Config.CELL_SIZE,
                segment[1] * Config.CELL_SIZE,
                Config.CELL_SIZE,
                Config.CELL_SIZE,
            )
            color = Config.SNAKE_HEAD_COLOR if index == 0 else Config.SNAKE_COLOR
            radius = 10 if index == 0 else 8
            pygame.draw.rect(screen, color, rect, border_radius=radius)


class FoodFactory:
    @staticmethod
    def create_food(snake_positions: List[Position]) -> Food:
        while True:
            position = (
                random.randint(0, Config.GRID_WIDTH - 1),
                random.randint(0, Config.GRID_HEIGHT - 1),
            )
            if position not in snake_positions:
                return Food(position)


class ScoreBoard:
    def __init__(self, font: pygame.font.Font, high_score_manager: HighScoreManager) -> None:
        self._font = font
        self._high_score_manager = high_score_manager

    def draw(self, screen: pygame.Surface, score: int) -> None:
        score_text = self._font.render(f"Score: {score}", True, Config.TEXT_COLOR)
        high_score_text = self._font.render(
            f"Best: {self._high_score_manager.high_score}",
            True,
            Config.TEXT_COLOR,
        )
        screen.blit(score_text, (10, 10))
        screen.blit(high_score_text, (10, 40))


class SnakeGame:
    def __init__(self) -> None:
        pygame.init()
        self._screen = pygame.display.set_mode((Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT))
        pygame.display.set_caption("Snake")
        self._clock = pygame.time.Clock()
        self._font_small = pygame.font.SysFont("arial", 28, bold=True)
        self._font_big = pygame.font.SysFont("arial", 70, bold=True)

        self._high_score_manager = HighScoreManager()
        self._scoreboard = ScoreBoard(self._font_small, self._high_score_manager)

        self._running = True
        self._game_over = False
        self._game_started = False
        self._score = 0

        self._snake = Snake((10, 10))
        self._food = FoodFactory.create_food(self._snake.body)

    @property
    def score(self) -> int:
        return self._score

    def restart(self) -> None:
        self._score = 0
        self._game_over = False
        self._snake = Snake((10, 10))
        self._food = FoodFactory.create_food(self._snake.body)

    def _draw_grid(self) -> None:
        for x in range(Config.GRID_WIDTH):
            for y in range(Config.GRID_HEIGHT):
                rect = pygame.Rect(
                    x * Config.CELL_SIZE,
                    y * Config.CELL_SIZE,
                    Config.CELL_SIZE,
                    Config.CELL_SIZE,
                )
                color = Config.LIGHT_COLOR if (x + y) % 2 == 0 else Config.DARK_COLOR
                pygame.draw.rect(self._screen, color, rect)

    def _draw_text_center(
        self,
        text: str,
        y: int,
        color: tuple[int, int, int],
        big: bool = False
    ) -> None:
        font = self._font_big if big else self._font_small
        outline_color = (0, 0, 0)

        base = font.render(text, True, color)
        outline = font.render(text, True, outline_color)
        rect = base.get_rect(center=(Config.WINDOW_WIDTH // 2, y))

        for dx in [-2, 2]:
            for dy in [-2, 2]:
                self._screen.blit(outline, (rect.x + dx, rect.y + dy))

        self._screen.blit(base, rect)

    def _draw_start_screen(self) -> None:
        self._screen.fill(Config.START_BG_COLOR)
        self._draw_text_center("SNAKE GAME", 200, Config.START_TITLE_COLOR, big=True)
        self._draw_text_center("Press S to start", 320, Config.START_TEXT_COLOR)
        self._draw_text_center("Press ESC to quit", 370, Config.START_SUBTEXT_COLOR)
        pygame.display.flip()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._running = False

                elif not self._game_started:
                    if event.key == pygame.K_s:
                        self._game_started = True

                elif self._game_over and event.key == pygame.K_r:
                    self.restart()

                elif not self._game_over:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self._snake.set_direction((0, -1))

                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self._snake.set_direction((0, 1))

                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        self._snake.set_direction((-1, 0))

                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        self._snake.set_direction((1, 0))

    def _update(self) -> None:
        if self._game_over or not self._game_started:
            return

        self._snake.move()

        if self._snake.collides_with_wall() or self._snake.collides_with_self():
            self._game_over = True
            self._high_score_manager.update_if_better(self._score)
            return

        if self._snake.head == self._food.position:
            self._score += 1
            self._snake.grow()
            self._food = FoodFactory.create_food(self._snake.body)
            self._high_score_manager.update_if_better(self._score)

    def _draw(self) -> None:
        if not self._game_started:
            self._draw_start_screen()
            return

        if self._game_over:
            self._screen.fill(Config.GAME_OVER_BG_COLOR)
            self._draw_text_center(
                "GAME OVER",
                Config.WINDOW_HEIGHT // 2 - 140,
                Config.GAME_OVER_COLOR,
                big=True,
            )
            self._draw_text_center(
                f"Your score: {self._score}",
                Config.WINDOW_HEIGHT // 2 + 10,
                Config.TEXT_COLOR,
            )
            self._draw_text_center(
                f"Best score: {self._high_score_manager.high_score}",
                Config.WINDOW_HEIGHT // 2 + 50,
                Config.TEXT_COLOR,
            )
            self._draw_text_center(
                "Press R to restart",
                Config.WINDOW_HEIGHT // 2 + 180,
                Config.TEXT_COLOR,
            )
            self._draw_text_center(
                "Press ESC to quit",
                Config.WINDOW_HEIGHT // 2 + 220,
                Config.TEXT_COLOR,
            )
            pygame.display.flip()
            return

        self._draw_grid()

        drawables: List[GameObject] = [self._food, self._snake]
        for obj in drawables:
            obj.draw(self._screen)

        self._scoreboard.draw(self._screen, self._score)

        pygame.display.flip()

    def run(self) -> None:
        while self._running:
            self._handle_events()
            self._update()
            self._draw()
            self._clock.tick(Config.FPS)

        pygame.quit()
        sys.exit()


def main() -> None:
    game = SnakeGame()
    game.run()


if __name__ == "__main__":
    main()