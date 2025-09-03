# ui/game_view.py - Main Game Display

## Purpose
The GameView class serves as the primary **View** component in the MVC architecture, responsible for all visual rendering of the chess game. It handles the main game loop, user interface display, and coordinates between user input and game logic through the GameController.

## Key Responsibilities
- Render the chess board and pieces
- Display game information (turn, move history, AI stats)
- Handle the main game loop and event processing
- Manage piece animations and visual effects
- Coordinate user input with game controller
- Draw UI elements (buttons, panels, text)

## Class Structure

### Instance Variables

#### Core Components
- `controller`: GameController instance for game logic coordination
- `constants`: ConstantValues instance for configuration
- `screen`: Pygame display surface for rendering
- `clock`: Pygame clock for frame rate control

#### Display Configuration
- `width`, `height`: Screen dimensions (512x512 for game board)
- `dimension`: Board size (8x8)
- `sq_size`: Individual square size (64 pixels)
- `max_fps`: Frame rate limit (15 FPS)
- `images`: Dictionary storing loaded piece images
- `colors`: Board color scheme [light_gray, dark_blue]

#### UI Elements
- `save_button`: Button for saving games
- `load_button`: Button for loading games
- `promote`: Flag for pawn promotion dialog state

**Why these variables?**
- Cached constants avoid repeated lookups
- Separate UI elements enable modular interface design
- Image dictionary prevents repeated file loading
- Clock ensures consistent frame rate across different hardware

## Key Methods

### Initialization and Setup

**`__init__()`**
- Initializes all display components and UI elements
- Sets up pygame display mode with side panel
- Creates controller instance for game logic
- Configures button positions and styling
- **Why**: Centralizes all initialization to ensure consistent setup

**`load_images()`**
- Loads all chess piece images from assets directory
- Scales images to match square size
- Creates placeholder rectangles if images missing
- Stores in images dictionary for fast access
- **Why**: Pre-loading prevents stuttering during gameplay

### Main Game Loop

**`main()`**
- Primary game loop handling all events and rendering
- **Process Flow**:
  1. Process pygame events (clicks, key presses, quit)
  2. Handle user input through controller
  3. Update game state
  4. Render current game state
  5. Process AI moves and animations
  6. Maintain consistent frame rate
- **Why**: Central coordination point for all game activity

### Event Handling

**Event Processing Logic**:
```python
for event in pygame.event.get():
    if event.type == QUIT:
        # Clean shutdown
    elif event.type == MOUSEBUTTONDOWN:
        # Handle clicks
    elif event.type == KEYDOWN:
        # Handle keyboard shortcuts
```

**Keyboard Shortcuts**:
- `K_z`: Undo last move
- `K_r`: Reset game to starting position
- `K_ESCAPE`: Return to main menu

**Why this approach**: Event-driven design ensures responsive interface and clean separation of concerns.

### Rendering System

**`draw_game_state(screen, valid_moves, sq_selected)`**
- Master rendering method coordinating all visual elements
- **Rendering Order**:
  1. Chess board squares
  2. Move highlights and selection
  3. Chess pieces
  4. Side panel information
- **Why**: Layered rendering ensures proper visual hierarchy

**`draw_board(screen)`**
- Renders alternating colored squares
- Uses modular arithmetic for checkerboard pattern: `(row + col) % 2`
- **Why**: Simple, efficient board rendering

**`draw_pieces(screen, board)`**
- Blits piece images onto board squares
- Skips empty squares (marked with "--")
- **Why**: Direct image blitting for optimal performance

### Visual Feedback System

**`highlight_squares(screen, valid_moves, sq_selected)`**
- Provides visual feedback for user interactions
- **Highlight Types**:
  - **Selected Square**: Blue overlay on chosen piece
  - **Valid Moves**: Light blue highlights on legal destinations
  - **Last Move**: Green highlight on most recent move
- **Implementation**: Semi-transparent surfaces for overlay effects
- **Why**: Essential UX feature helping users understand game state

### Side Panel Display

**`draw_side_panel(screen)`**
- Renders information panel with multiple components
- **Components**:
  - Turn indicator
  - Move history
  - AI performance statistics
  - Save/load buttons
- **Why**: Provides game context without cluttering board

**`draw_turn_indicator(screen)`**
- Shows whose turn it is with colored rectangle
- White background for white's turn, black for black's turn
- Includes text label for clarity
- **Why**: Clear visual indication of current player

**`draw_move_log(screen)`**
- Displays recent move history in algebraic notation
- Shows last 12 moves in 4-column grid
- **Format**: "e2e4," style notation
- **Why**: Helps players track game progress and review moves

**`draw_ai_stats(screen)`**
- Shows real-time AI performance metrics
- **Metrics Displayed**:
  - Number of AI moves made
  - Average thinking time
  - Current search depth
  - Nodes searched per second
- **Why**: Provides insight into AI thinking process and performance

### Animation System

**`animate_move(move, screen, board, clock)`**
- Smoothly animates piece movement between squares
- **Animation Process**:
  1. Calculate movement delta (dR, dC)
  2. Determine frame count based on distance
  3. Interpolate piece position over multiple frames
  4. Redraw board and pieces each frame
  5. Handle captured pieces and special moves
- **Frame Rate**: 60 FPS during animation for smoothness
- **Why**: Visual feedback makes moves clear and game more engaging

### User Interface Components

**`draw_save_buttons(save_button, load_button, screen)`**
- Renders clickable save and load buttons
- Buttons positioned in side panel area
- **Why**: Provides easy access to game persistence features

**`check_save_buttons(location)`**
- Processes clicks on save/load buttons
- Calls appropriate controller methods
- **Why**: Bridges UI clicks to game functionality

### Special UI Handling

**`draw_text(screen, text)`**
- Displays centered text messages
- Used for game over conditions (checkmate, stalemate)
- **Styling**: Large, bold font with centered positioning
- **Why**: Important game state messages need prominent display

**`draw_pawn_promotion()`**
- Handles pawn promotion piece selection
- **Process**:
  1. Creates promotion piece buttons (Q, R, B, N)
  2. Enters modal loop until selection made
  3. Passes choice to controller
  4. Returns to main game loop
- **Why**: Pawn promotion requires user input, blocking other actions

## Design Patterns Used

### Model-View-Controller (MVC)
GameView serves as the View, communicating with GameController (Controller) which manages GameState (Model).

### Observer Pattern
GameView observes game state changes through controller interface and updates display accordingly.

### State Pattern
Different rendering modes (normal play, pawn promotion, game over) represent different UI states.

### Command Pattern
User inputs are translated into controller method calls.

## Performance Considerations

### Frame Rate Management
- Limited to 15 FPS during normal play
- Increased to 60 FPS during animations
- **Why**: Balances smooth visuals with CPU efficiency

### Image Caching
- All piece images loaded once at startup
- Stored in dictionary for O(1) access
- **Why**: Prevents file I/O during gameplay

### Efficient Rendering
- Only redraws when game state changes
- Uses pygame's optimized blitting functions
- **Why**: Maintains consistent performance

## Integration Points

### Controller Communication
```python
# Input handling
self.controller.handle_mouse_click(location)

# State queries
valid_moves = self.controller.get_valid_moves()
board = self.controller.get_board()

# Game management
self.controller.save_game()
```

### Menu System Integration
- Can return to menu system via ESC key
- Creates MainMenu instance when needed
- **Why**: Seamless navigation between game and menus

## Error Handling

### Missing Assets
- Creates placeholder rectangles if piece images missing
- Continues functioning with reduced visual quality
- **Why**: Graceful degradation prevents crashes

### Display Errors
- Handles pygame initialization failures
- Provides error messages for debugging
- **Why**: Robust error handling improves user experience

## Threading Considerations
GameView runs in the main thread while AI calculations occur in background threads. The view polls for AI completion rather than using callbacks to avoid threading issues with pygame.

## Future Enhancement Opportunities

### Visual Improvements
- **Board Themes**: Multiple color schemes
- **Piece Sets**: Different piece artwork styles
- **Animations**: More sophisticated move animations
- **Highlights**: Improved visual feedback system

### UI Enhancements
- **Resizable Window**: Dynamic layout adjustment
- **Settings Panel**: In-game configuration options
- **Analysis Mode**: Position evaluation display
- **Game Browser**: Visual save file selection

### Performance Optimizations
- **Dirty Rectangle Updates**: Only redraw changed areas
- **Sprite Groups**: Pygame sprite system for piece management
- **Hardware Acceleration**: OpenGL rendering for complex effects

The GameView provides a clean, functional interface that effectively bridges user interactions with the chess engine while maintaining good performance and visual appeal.