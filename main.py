from game import SnakeGame


def main() -> None:
    game = SnakeGame()
    game.run()


if __name__ == "__main__":
    main()
    from pathlib import Path

class Config:
    WINDOW_WIDTH = 600
    WINDOW_HEIGHT = 600
    CELL_SIZE = 20
    GRID_WIDTH = WINDOW_WIDTH // CELL_SIZE
    GRID_HEIGHT = WINDOW_HEIGHT // CELL_SIZE
    FPS = 10

    BACKGROUND_COLOR = (20, 20, 20)
    LIGHT_COLOR = (50, 50, 50)
    DARK_COLOR = (30, 30, 30)

    SNAKE_COLOR = (0, 200, 0)
    FOOD_COLOR = (220, 40, 40)
    TEXT_COLOR = (255, 255, 255)
    GAME_OVER_COLOR = (255, 210, 0)

    HIGH_SCORE_FILE = Path("highscore.txt")
    from __future__ import annotations

import random
from abc import ABC, abstractmethod
from typing import List, Tuple

import pygame

from config import Config

Position = Tuple[int, int]


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
    def draw(self, surface: pygame.Surface) -> None:
        pass



class Food(GameObject):
    def draw(self, surface: pygame.Surface) -> None:
        rect = pygame.Rect(
            self._position[0] * Config.CELL_SIZE,
            self._position[1] * Config.CELL_SIZE,
            Config.CELL_SIZE,
            Config.CELL_SIZE,
        )
        pygame.draw.rect(surface, Config.FOOD_COLOR, rect)


class FoodFactory:
    @staticmethod
    def create_food(snake_positions: List[Position]) -> Food:
        available_positions = [
            (x, y)
            for x in range(Config.GRID_WIDTH)
            for y in range(Config.GRID_HEIGHT)
            if (x, y) not in snake_positions
        ]

        if not available_positions:
            return Food((0, 0))

        return Food(random.choice(available_positions))


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
        head_x, head_y = self.head
        dx, dy = self._direction
        new_head = (head_x + dx, head_y + dy)

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

    def draw(self, surface: pygame.Surface) -> None:
        for segment in self._body:
            rect = pygame.Rect(
                segment[0] * Config.CELL_SIZE,
                segment[1] * Config.CELL_SIZE,
                Config.CELL_SIZE,
                Config.CELL_SIZE,
            )
            pygame.draw.rect(surface, Config.SNAKE_COLOR, rect)           
    import pygame

from config import Config


class HighScoreManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._high_score = 0
            cls._instance._load_high_score()
        return cls._instance

    def _load_high_score(self) -> None:
        if Config.HIGH_SCORE_FILE.exists():
            try:
                value = Config.HIGH_SCORE_FILE.read_text(encoding="utf-8").strip()
                self._high_score = int(value) if value else 0
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


class ScoreBoard:
    def __init__(self, font: pygame.font.Font, high_score_manager: HighScoreManager) -> None:
        self._font = font
        self._high_score_manager = high_score_manager

    def draw(self, surface: pygame.Surface, score: int) -> None:
        score_text = self._font.render(f"Score: {score}", True, Config.TEXT_COLOR)
        high_text = self._font.render(
            f"Best: {self._high_score_manager.high_score}",
            True,
            Config.TEXT_COLOR,
        )
        surface.blit(score_text, (10, 10))
        surface.blit(high_text, (10, 40))