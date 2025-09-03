# main.py - Entry Point

## Purpose
This is the entry point for the chess application. It initializes the game and launches the main menu system. This file follows the standard Python convention of using `if __name__ == "__main__":` to ensure the code only runs when the file is executed directly, not when imported as a module.

## Structure
```python
if __name__ == "__main__":
    from ui.game_view import GameView
    from ui.menu_system import MainMenu
    
    game = GameView()
    menu = MainMenu(game)
    menu.draw_main_menu()
```

## Components

### Imports
- **GameView**: Main game display and rendering engine
- **MainMenu**: Menu system for navigation and game mode selection

### Execution Flow
1. Creates a `GameView` instance that handles the main game display
2. Creates a `MainMenu` instance, passing the game view as a dependency
3. Launches the main menu interface

## Why This Design
- **Separation of Concerns**: Keeps the entry point minimal and delegates functionality to specialized classes
- **Dependency Injection**: The menu system receives the game view, allowing it to launch the game when needed
- **Standard Python Pattern**: Uses the `__main__` guard to make the file both importable and executable

## Variables
- `game`: Instance of GameView class responsible for rendering and game loop
- `menu`: Instance of MainMenu class responsible for navigation and mode selection

## Design Pattern
This follows the **Facade Pattern** where the main file provides a simple interface to start the complex chess application system.