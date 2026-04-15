import unittest

from main import FoodFactory, HighScoreManager, Snake


class TestSnake(unittest.TestCase):
    def test_snake_moves_right_by_default(self):
        snake = Snake((5, 5))
        snake.move()
        self.assertEqual(snake.head, (6, 5))

    def test_snake_grows_after_eating(self):
        snake = Snake((5, 5))
        snake.grow()
        snake.move()
        self.assertEqual(len(snake.body), 2)

    def test_snake_cannot_reverse_direction(self):
        snake = Snake((5, 5))
        snake.set_direction((-1, 0))
        snake.move()
        self.assertEqual(snake.head, (6, 5))

    def test_food_factory_does_not_spawn_inside_snake(self):
        snake_positions = [(1, 1), (2, 1), (3, 1)]
        food = FoodFactory.create_food(snake_positions)
        self.assertNotIn(food.position, snake_positions)

    def test_high_score_manager_is_singleton(self):
        manager1 = HighScoreManager()
        manager2 = HighScoreManager()
        self.assertIs(manager1, manager2)


if __name__ == "__main__":
    unittest.main()