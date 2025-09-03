# controllers/game_controller.py - Game Controller

## Purpose
The GameController serves as the central orchestrator for the chess game, managing game flow, user input, AI interactions, and coordination between different game components. It implements the **Controller** in the MVC (Model-View-Controller) pattern, handling business logic and user interactions.

## Key Responsibilities
- Process user input (mouse clicks, keyboard commands)
- Manage game modes (Human vs Human, Human vs AI, AI vs AI)
- Coordinate AI move calculations and threading
- Handle special moves (castling, en passant, pawn promotion)
- Manage game state transitions and move validation
- Provide interface between UI and core game logic

## Class Structure

### Instance Variables

#### Core Components
- `constants`: Instance of ConstantValues for game constants
- `game_state`: Instance of GameState managing the chess position
- `ai`: Instance of AdvancedChessAI for computer opponent
- `save_manager`: Instance of SaveManager for game persistence

#### Game State Variables
- `valid_moves`: List of legal moves in current position
- `sq_size`: Size of board squares for UI calculations
- `move_made`: Boolean flag indicating if a move was just made
- `animate_move`: Boolean flag for move animation
- `game_over`: Boolean flag for game end state
- `sq_selected`: Tuple (row, col) of currently selected square
- `player_clicks`: List of player click coordinates

#### AI Threading Variables
- `return_queue`: Queue for AI move results from separate thread
- `ai_is_thinking`: Boolean flag indicating AI calculation in progress
- `move_find_thread`: Thread object for AI move calculation
- `undo_move_flag`: Flag to handle move undo during AI calculation

#### Game Mode Settings
- `player_one`: Boolean - True if white player is human
- `player_two`: Boolean - True if black player is human  
- `random_turn`: Boolean - True if using random moves
- `promote`: Boolean - UI flag for pawn promotion dialog

#### AI Configuration
- `ai_time_limit`: Maximum time AI can spend on move (seconds)
- `ai_depth`: Maximum search depth for AI
- `total_ai_time`: Cumulative time spent by AI
- `ai_moves_made`: Counter of AI moves for statistics

## Key Methods

### Game Mode Setters
These methods configure different playing modes:

**`set_player_vs_player()`**
- Sets both players as human
- Disables AI and random moves
- Used for traditional two-player chess

**`set_ai_vs_ai()`**
- Sets both players as AI
- Creates AI vs AI demonstration mode
- Useful for testing and entertainment

**`set_ai_black()`**
- Human plays white, AI plays black
- Most common single-player mode
- Follows chess convention of white moving first

**`set_ai_white()`**
- AI plays white, human plays black
- Alternative single-player mode
- AI gets first move advantage

**`set_random_vs_ai()`**
- One side plays random moves, other uses AI
- Used for testing AI against weak opponent
- Educational/demonstration purposes

### Input Handling Methods

**`handle_mouse_click(location)`**
- Processes mouse clicks on the chess board
- Converts pixel coordinates to board coordinates
- Manages piece selection and move execution
- Handles two-click move interface (select piece, select destination)
- Validates moves against legal move list
- Why: Provides intuitive click-to-move interface

**`handle_random_move()`**
- Executes random legal moves when in random mode
- Uses AI's random move generator for fair selection
- Automatic move execution without user input
- Why: Enables automated play for testing/demonstration

### Move Management

**`undo_move()`**
- Reverts the last move made
- Cancels ongoing AI calculations if needed
- Updates game state and UI flags
- Handles thread synchronization safely
- Why: Essential feature for game analysis and correction

**`handle_ai_move()`**
- Manages AI move calculation and execution
- Handles threading for non-blocking AI computation
- Configures AI parameters based on game stage
- Processes AI move results from background thread
- Includes fallback to random moves if AI fails
- Why: Enables computer opponent functionality

### AI Configuration

**`configure_ai_for_position()`**
- Adjusts AI parameters based on current game stage
- Opening: Shorter time, lower depth for known theory
- Middlegame: Standard parameters for complex positions  
- Endgame: Extended time and depth for precise calculation
- Uses piece count to determine game stage
- Why: Optimizes AI performance for different game phases

**`set_ai_difficulty(level)`**
- Sets AI strength parameters (1=Easy, 2=Normal, 3=Hard)
- Adjusts search depth and time limits
- Easy: Depth 4, 2 seconds
- Normal: Depth 6, 5 seconds  
- Hard: Depth 8, 10 seconds
- Why: Provides adjustable challenge levels

### Game State Management

**`process_moves(screen, clock, view)`**
- Coordinates move execution with UI updates
- Handles move animation timing
- Updates valid moves after each move
- Checks for game end conditions (checkmate/stalemate)
- Displays appropriate game end messages
- Why: Synchronizes game logic with visual presentation

**`reset_game()`**
- Resets all game state to starting position
- Cancels ongoing AI calculations
- Clears transposition table and statistics
- Reinitializes all flags and counters
- Why: Allows starting fresh games

### Utility Methods

**`needs_pawn_promotion()`**
- Checks if the last move was a pawn promotion
- Returns boolean for UI pawn promotion dialog
- Why: Determines when to show promotion piece selection

**`get_ai_stats()`**
- Returns dictionary of AI performance metrics
- Includes move count, average time, search statistics
- Used for displaying real-time AI information
- Why: Provides insight into AI thinking process

**`get_position_analysis()`**
- Provides quick analysis of current position
- Returns material balance, piece count, game stage
- Includes position evaluation score
- Why: Gives players insight into position strength

## Design Patterns Used

### Observer Pattern
The controller observes game state changes and notifies the UI components.

### Command Pattern  
Input handling methods encapsulate user actions as operations.

### State Pattern
Game mode variables represent different behavioral states of the controller.

### Strategy Pattern
Different AI difficulty levels represent different strategic approaches.

## Threading Considerations
The controller manages AI calculations in separate threads to prevent UI freezing:
- Uses `queue.Queue` for thread-safe communication
- Implements proper thread cleanup and cancellation
- Handles timeout scenarios gracefully
- Ensures UI remains responsive during AI calculations

## Why This Design
The GameController centralizes game flow management while keeping components loosely coupled. It provides a clean interface between the UI and core game logic, making the system modular and testable. The threading implementation ensures smooth user experience even during intensive AI calculations.