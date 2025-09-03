# core/move.py - Move Representation

## Purpose
This module defines the Move and CastleRights classes, which represent chess moves and castling permissions respectively. The Move class serves as a complete record of a chess move with all information needed for execution and undo operations.

## Classes

### CastleRights Class

**Purpose**: Tracks which castling moves are still legal for both sides.

#### Instance Variables
- `wks`: Boolean - White kingside castling allowed
- `bks`: Boolean - Black kingside castling allowed  
- `wqs`: Boolean - White queenside castling allowed
- `bqs`: Boolean - Black queenside castling allowed

#### Methods
**`__eq__(other)`**
- Compares two CastleRights objects for equality
- Returns True if all four castling rights match
- Why: Needed for game state comparison and undo operations

**`copy()`**
- Creates an independent copy of the castling rights
- Returns new CastleRights with same permission values
- Why: Prevents accidental modification of historical state

### Move Class

**Purpose**: Represents a single chess move with complete information for execution and undo.

#### Class Variables (Coordinate Conversion)
- `ranks_to_rows`: Dictionary mapping chess ranks ("1"-"8") to array indices (7-0)
- `rows_to_ranks`: Reverse mapping from array indices to chess ranks
- `files_to_cols`: Dictionary mapping chess files ("a"-"h") to array indices (0-7)  
- `cols_to_files`: Reverse mapping from array indices to chess files
- Why: Enables conversion between chess notation and internal coordinates

#### Instance Variables

##### Basic Move Information
- `start_row`, `start_col`: Starting position coordinates (0-7)
- `end_row`, `end_col`: Ending position coordinates (0-7)
- `piece_moved`: String representation of moving piece (e.g., "wK", "bp")
- `piece_captured`: String representation of captured piece or "--" if none
- Why: Essential information to execute any chess move

##### Special Move Flags
- `enPassant`: Boolean indicating en passant capture
- `pawn_promotion`: Boolean indicating pawn promotion
- `is_castle_move`: Boolean indicating castling move
- Why: Chess has special moves requiring different execution logic

##### Undo Information
- `promoted_to`: String indicating what piece pawn promoted to
- `last_moved`: Integer turn number when this move was made
- `castle_rights_before`: CastleRights object before this move
- `en_passant_before`: En passant state before this move
- `fifty_move_counter`: Counter for fifty-move rule
- Why: Complete undo requires restoring all affected game state

##### Move Identification
- `move_id`: Unique integer identifier based on coordinates
- `special_id`: Enhanced identifier including special move types
- Why: Enables fast move comparison and hash table usage

## Key Methods

### Initialization
**`__init__(start_sq, end_sq, board, enPassant=False, pawn_promotion=False, is_castle_move=False)`**
- Creates Move object with basic information
- Extracts piece information from board position
- Handles en passant captured piece logic (piece isn't on target square)
- Generates unique identifiers for the move
- Initializes undo information storage
- Why: Comprehensive move creation with all necessary data

### Special Move Identification
**`get_special_id()`**
- Creates unique identifier including move type information
- Incorporates piece types and special move flags
- Uses ASCII values for uniqueness
- Why: Enables advanced move comparison and caching

### State Storage for Undo
**`set_promotion_piece(piece)`**
- Stores what piece the pawn promoted to
- Called after promotion piece is selected
- Why: Undo needs to know what piece to remove

**`set_castle_rights_before(castle_rights)`**
- Stores castling rights state before move execution
- Makes independent copy to prevent modification
- Why: Castling rights often change after moves

**`set_en_passant_before(en_passant_square)`**
- Stores en passant state before move
- Why: En passant availability changes frequently

**`set_last_moved(turn)`**
- Records when this piece last moved
- Used for UI highlighting and analysis
- Why: Provides move timing information

### Comparison and Hashing
**`__eq__(other)`**
- Compares moves for equality
- Considers coordinates, piece types, and special move flags
- Returns False for non-Move objects
- Why: Essential for move validation and list operations

**`__hash__()`**
- Generates hash value for use in sets and dictionaries
- Includes all move-defining characteristics
- Why: Enables efficient move storage and lookup

### Notation and Display
**`get_chess_notation()`**
- Returns move in algebraic notation (e.g., "e2e4")
- Uses coordinate conversion dictionaries
- Why: Standard chess notation for display and export

**`get_rank_file(r, c)`**
- Converts internal coordinates to chess notation
- Helper method for notation generation
- Why: Reusable coordinate conversion

### Validation
**`is_valid()`**
- Checks if move coordinates are within board bounds
- Verifies moving piece exists (not "--")
- Why: Basic sanity checking for move validity

### String Representation
**`__str__()`**
- User-friendly string representation
- Shows move notation and piece information
- Why: Helpful for debugging and display

**`__repr__()`**
- Detailed string representation for debugging
- Shows all internal move data
- Why: Complete information for development

## Design Decisions

### Immutable Design
Once created, Move objects shouldn't be modified except for undo information storage. This prevents accidental corruption of move history.

### Complete Information Storage
The Move class stores everything needed to execute and undo the move, making the system robust and enabling complex features like position analysis.

### Multiple Identification Methods
Both simple coordinate-based and enhanced special-move-aware identification enables different use cases (fast lookup vs. precise matching).

### Chess Notation Integration
Built-in conversion between internal coordinates and standard chess notation makes the system interoperable with chess tools and databases.

## Usage Patterns

### Move Creation
```python
move = Move((6, 4), (4, 4), board)  # e2-e4
```

### Move Validation
```python
if attempted_move in valid_moves:
    game_state.make_move(attempted_move)
```

### Move History
```python
for move in move_log:
    print(move.get_chess_notation())
```

### Undo Preparation
```python
move.set_castle_rights_before(current_rights)
move.set_en_passant_before(en_passant_state)
```

This design enables robust move handling with complete information for both execution and undo, supporting advanced chess features while maintaining clean, readable code.