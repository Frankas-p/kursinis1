# Snake OOP Coursework

## Introduction

This project is a Snake game developed in Python using the pygame library.
The main goal of this project is to demonstrate and apply object-oriented programming (OOP) principles in a practical application.

The game allows the player to control a snake, collect food, and increase their score. The highest score is saved to a file and persists between game sessions.
The program also includes a start screen and a game over screen to improve user experience.

---

## How to run the program

1. Install Python (version 3.10 or higher)
2. Install pygame:

```
pip install pygame
```

3. Run the game:

```
py main.py
```

---

## How to use the program

* Press **S** to start the game
* Move the snake using:

  * Arrow keys OR W, A, S, D
* Collect food to increase score
* Avoid hitting walls or yourself
* Press **R** to restart after game over
* Press **ESC** to quit

---

## Body / Analysis

### Object-Oriented Programming principles

#### Encapsulation

Encapsulation is implemented by restricting direct access to class attributes and using controlled access through methods and properties.
For example, the `Snake` class uses protected attributes such as `_body` and `_direction`.

#### Inheritance

Inheritance is implemented through the `GameObject` abstract class.
Both `Snake` and `Food` classes inherit from it and reuse shared structure and behavior.

#### Polymorphism

Polymorphism is demonstrated by the `draw()` method.
Different classes (`Snake` and `Food`) implement this method differently, but they are used in the same way within the game loop.

#### Abstraction

Abstraction is achieved using the `GameObject` abstract base class.
It defines a common interface (`draw()` method) that all game objects must implement.

---

### Design Pattern

#### Singleton Pattern

The `HighScoreManager` class uses the Singleton pattern.
This ensures that only one instance of the high score manager exists during the program execution and is shared across the entire application.

This is useful because:

* it provides a single source of truth for the high score
* prevents data inconsistency
* simplifies file handling

---

### Composition and Aggregation

* The `Snake` class uses composition, as it is made up of multiple body segments.
* The `SnakeGame` class uses aggregation by containing and managing objects such as `Snake`, `Food`, and `ScoreBoard`.

---

### File Reading and Writing

The program saves the best score in a file called `highscore.txt`.

* The score is loaded when the program starts
* The score is updated and saved when a new high score is achieved

---

### Testing

Unit tests are implemented using the `unittest` framework.

The tests cover:

* snake movement
* snake growth
* direction logic
* food spawning
* singleton behavior

Tests can be run with:

```
py -m unittest test_snake.py
```

---

## Results

* The Snake game was successfully implemented using object-oriented programming principles.
* The program includes persistent high score storage using file handling.
* The use of design patterns improved code organization and maintainability.
* The game includes separate start and game over screens, improving the user interface.
* Some challenges included handling movement logic and fixing indentation issues in Python.

---

## Conclusions

The project achieved its main goal of applying OOP principles in a practical program.
The Snake game clearly demonstrates encapsulation, inheritance, polymorphism, and abstraction.

The final result is a functional and interactive game with improved visuals and user experience.

In the future, the application could be extended by:

* adding sound effects
* implementing levels or increasing difficulty
* improving graphics and animations
* adding a more advanced menu system

---

## References

* Python documentation: https://docs.python.org
* Pygame documentation: https://www.pygame.org/docs/
