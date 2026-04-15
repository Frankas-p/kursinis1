import pygame
import random
from pathlib import Path
from typing import Tuple

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

    SNAKE_COLOR = (0, 200, 0)
    FOOD_COLOR = (220, 40, 40)
    TEXT_COLOR = (255, 255, 255)
    GAME_OVER_COLOR = (255, 210, 0)

    HIGH_SCORE_FILE = Path("highscore.txt")


class HighScoreManager:
    def __init__(self) -> None:
        self.high_score = self.load_high_score()

    def load_high_score(self) -> int:
        if Config.HIGH_SCORE_FILE.exists():
            try:
                text = Config.HIGH_SCORE_FILE.read_text(encoding="utf-8").strip()
                return int(text) if text else 0
            except (ValueError, OSError):
                return 0
        return 0

    def save_high_score(self) -> None:
        Config.HIGH_SCORE_FILE.write_text(str(self.high_score), encoding="utf-8")

    def update_if_better(self, score: int) -> None:
        if score > self.high_score:
            self.high_score = score
            self.save_high_score()


class Snake:
    def __init__(self, position: Position) -> None:
        self.body = [position]
        self.direction = (1, 0)
        self.grow_pending = 0

    @property
    def head(self) -> Position:
        return self.body[0]

    def set_direction(self, new_direction: Position) -> None:
        opposite = (-self.direction[0], -self.direction[1])
        if new_direction != opposite:
            self.direction = new_direction

    def move(self) -> None:
        x, y = self.head
        dx, dy = self.direction
        new_head = (x + dx, y + dy)

        self.body.insert(0, new_head)

        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()

    def grow(self) -> None:
        self.grow_pending += 1

    def collides_with_self(self) -> bool:
        return self.head in self.body[1:]

    def collides_with_wall(self) -> bool:
        x, y = self.head
        return not (0 <= x < Config.GRID_WIDTH and 0 <= y < Config.GRID_HEIGHT)

    def draw(self, screen: pygame.Surface) -> None:
        for segment in self.body:
            rect = pygame.Rect(
                segment[0] * Config.CELL_SIZE,
                segment[1] * Config.CELL_SIZE,
                Config.CELL_SIZE,
                Config.CELL_SIZE,
            )
            pygame.draw.rect(screen, Config.SNAKE_COLOR, rect)


class Food:
    def __init__(self, position: Position) -> None:
        self.position = position

    def draw(self, screen: pygame.Surface) -> None:
        rect = pygame.Rect(
            self.position[0] * Config.CELL_SIZE,
            self.position[1] * Config.CELL_SIZE,
            Config.CELL_SIZE,
            Config.CELL_SIZE,
        )
        pygame.draw.rect(screen, Config.FOOD_COLOR, rect)


class SnakeGame:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT))
        pygame.display.set_caption("Snake")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 28)

        self.high_score_manager = HighScoreManager()

        self.running = True
        self.game_over = False
        self.score = 0

        self.snake = Snake((10, 10))
        self.food = self.create_food()

    def create_food(self) -> Food:
        while True:
            position = (
                random.randint(0, Config.GRID_WIDTH - 1),
                random.randint(0, Config.GRID_HEIGHT - 1),
            )
            if position not in self.snake.body:
                return Food(position)

    def restart(self) -> None:
        self.score = 0
        self.game_over = False
        self.snake = Snake((10, 10))
        self.food = self.create_food()

    def draw_grid(self) -> None:
        for x in range(Config.GRID_WIDTH):
            for y in range(Config.GRID_HEIGHT):
                rect = pygame.Rect(
                    x * Config.CELL_SIZE,
                    y * Config.CELL_SIZE,
                    Config.CELL_SIZE,
                    Config.CELL_SIZE,
                )

                if (x + y) % 2 == 0:
                    color = Config.LIGHT_COLOR
                else:
                    color = Config.DARK_COLOR

                pygame.draw.rect(self.screen, color, rect)

    def draw_text_center(self, text: str, y: int, color: tuple[int, int, int]) -> None:
        rendered = self.font.render(text, True, color)
        rect = rendered.get_rect(center=(Config.WINDOW_WIDTH // 2, y))
        self.screen.blit(rendered, rect)

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

                elif self.game_over and event.key == pygame.K_r:
                    self.restart()

                elif not self.game_over:
                    if event.key == pygame.K_UP:
                        self.snake.set_direction((0, -1))
                    elif event.key == pygame.K_DOWN:
                        self.snake.set_direction((0, 1))
                    elif event.key == pygame.K_LEFT:
                        self.snake.set_direction((-1, 0))
                    elif event.key == pygame.K_RIGHT:
                        self.snake.set_direction((1, 0))

    def update(self) -> None:
        if self.game_over:
            return

        self.snake.move()

        if self.snake.collides_with_wall() or self.snake.collides_with_self():
            self.game_over = True
            self.high_score_manager.update_if_better(self.score)
            return

        if self.snake.head == self.food.position:
            self.score += 1
            self.snake.grow()
            self.food = self.create_food()
            self.high_score_manager.update_if_better(self.score)

    def draw_score(self) -> None:
        score_text = self.font.render(f"Score: {self.score}", True, Config.TEXT_COLOR)
        high_score_text = self.font.render(
            f"Best: {self.high_score_manager.high_score}",
            True,
            Config.TEXT_COLOR,
        )
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(high_score_text, (10, 40))

    def draw(self) -> None:
        self.draw_grid()
        self.snake.draw(self.screen)
        self.food.draw(self.screen)
        self.draw_score()

        if self.game_over:
            self.draw_text_center("GAME OVER", Config.WINDOW_HEIGHT // 2 - 40, Config.GAME_OVER_COLOR)
            self.draw_text_center("Press R to restart", Config.WINDOW_HEIGHT // 2, Config.TEXT_COLOR)
            self.draw_text_center("Press ESC to quit", Config.WINDOW_HEIGHT // 2 + 40, Config.TEXT_COLOR)

        pygame.display.flip()

    def run(self) -> None:
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(Config.FPS)

        pygame.quit()


def main() -> None:
    game = SnakeGame()
    game.run()


if __name__ == "__main__":
    main()