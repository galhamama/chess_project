# core/constants.py - Game Constants

## Purpose
The ConstantValues class centralizes all configuration values, display settings, and game constants used throughout the chess application. This follows the **Single Responsibility Principle** and **Don't Repeat Yourself (DRY)** principles by providing a single source of truth for all constant values.

## Key Benefits
- **Maintainability**: Change display settings in one place
- **Consistency**: Ensures uniform values across all modules
- **Configuration**: Easy adjustment of game parameters
- **Readability**: Named constants instead of magic numbers

## Class Structure

### Screen and Display Settings

#### Window Dimensions
- `WIDTH`: Integer (512) - Main game board width in pixels
- `HEIGHT`: Integer (WIDTH) - Game board height (square aspect ratio)
- `SIDE_SCREEN`: Integer (200) - Width of side panel for UI elements
- `MENU_OFFSET`: Float (SIDE_SCREEN / 2) - Centering offset for menu buttons

**Why these values?**
- 512x512 provides clean 64x64 pixel squares (512/8 = 64)
- Square aspect ratio matches chess board proportions
- Side panel provides space for game information without crowding
- Menu offset centers UI elements in available space

#### Board Configuration  
- `DIMENSION`: Integer (8) - Chess board size (8x8 squares)
- `SQ_SIZE`: Integer (HEIGHT // DIMENSION) - Size of each board square in pixels
- `MAX_FPS`: Integer (15) - Maximum frames per second for game loop

**Why these values?**
- 8x8 is standard chess board size
- Square size calculated to fit exactly in window (64 pixels each)
- 15 FPS provides smooth animation without excessive CPU usage

#### Image Storage
- `IMAGE`: Dictionary ({}) - Container for loaded piece images
- Why: Centralized storage prevents reloading images multiple times

### Board Representation Constants

#### Piece Notation
- `EMPTY_POSITION`: String ("--") - Represents empty board squares
- `WHITE_PLAYER`: String ('w') - Identifier for white pieces
- `BLACK_PLAYER`: String ('b') - Identifier for black pieces

**Why this notation?**
- Two-character system: first char = color, second char = piece type
- "--" is visually distinct from piece notation
- Single character color codes for compact representation
- Follows chess programming conventions

### Color Definitions

#### Board Colors
- `LIGHT_GRAY`: RGB Tuple (126, 135, 152) - Light squares on chess board
- `DARK_BLUE`: RGB Tuple (43, 50, 64) - Dark squares on chess board
- `DIM_BLUE`: RGB Tuple (21, 28, 41) - Background and side panel color

**Color Choice Rationale:**
- High contrast between light and dark squares for clarity
- Blue theme provides modern, professional appearance
- Colors are easy on the eyes during extended play

#### UI Colors
- `WHITE`: RGB Tuple (255, 255, 255) - Pure white for text and highlights
- `BLACK`: RGB Tuple (0, 0, 0) - Pure black for text and contrast
- `DARK_GRAY`: RGB Tuple (36, 36, 36) - Button backgrounds and UI elements

**Why these colors?**
- Pure white/black provide maximum contrast for readability
- Dark gray complements the blue theme while remaining neutral
- All colors maintain good accessibility contrast ratios

## Design Patterns Used

### Singleton-like Pattern
While not a true singleton, ConstantValues is typically instantiated once and shared across components, providing global access to constants.

### Configuration Object Pattern
All related configuration is grouped in a single class, making it easy to modify and extend.

## Usage Patterns

### Typical Instantiation
```python
self.constants = ConstantValues()
```

### Common Access Patterns
```python
# Screen dimensions
screen = pygame.display.set_mode((self.constants.WIDTH + self.constants.SIDE_SCREEN, self.constants.HEIGHT))

# Board iteration  
for row in range(self.constants.DIMENSION):
    for col in range(self.constants.DIMENSION):
        # Process each square

# Color usage
pygame.draw.rect(screen, self.constants.LIGHT_GRAY, square_rect)

# Empty square checking
if board[row][col] == self.constants.EMPTY_POSITION:
    # Square is empty
```

## Extensibility
The class can be easily extended for additional features:
- Sound settings
- Different board themes  
- Animation speeds
- AI difficulty parameters
- Language settings

## Alternative Approaches Considered

### Global Variables
Could use module-level constants, but class-based approach provides:
- Better organization
- Easier testing
- Clear ownership
- Extension capabilities

### Configuration Files
Could load from JSON/INI files, but built-in constants provide:
- Faster startup
- No file I/O dependencies
- Type safety
- IDE support

### Enums
Could use Python enums for some values, but current approach provides:
- Simpler implementation
- Direct value access
- Better pygame integration

## Design Philosophy
This constants file reflects several design principles:
1. **Centralization**: All constants in one logical place
2. **Calculation**: Derived values computed automatically
3. **Naming**: Clear, descriptive constant names
4. **Grouping**: Related constants organized together
5. **Immutability**: Values set once at initialization

The approach balances simplicity with maintainability, providing a clean foundation for the chess application's configuration management.