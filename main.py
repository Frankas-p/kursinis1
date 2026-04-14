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
    SNAKE_COLOR = (0, 200, 0)
    FOOD_COLOR = (220, 40, 40)
    TEXT_COLOR = (255, 255, 255)
    GAME_OVER_COLOR = (255, 210, 0)

    HIGH_SCORE_FILE = Path("highscore.txt")