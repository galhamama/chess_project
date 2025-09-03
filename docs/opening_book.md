# ai/opening_book.py - Chess Opening Database

## Purpose
The OpeningBook class provides a comprehensive database of popular chess openings to improve the AI's early game performance. Instead of calculating moves from scratch in well-known positions, the AI can instantly play strong, principled opening moves based on centuries of chess theory.

## Key Benefits
- **Faster Opening Play**: Instant move selection instead of calculation
- **Stronger Opening Theory**: Plays established, sound openings
- **Educational Value**: Exposes players to classical opening principles
- **Performance Optimization**: Saves computation time for complex middlegame positions

## Class Structure

### Instance Variables

#### Core Data Storage
- `book`: Dictionary mapping FEN positions to move lists
- `max_depth`: Maximum number of opening moves to follow (default: 12)
- `opening_lines`: Dictionary of position strings to move options

#### Opening Database Format
```python
position_fen: [
    (move_notation, weight, opening_name),
    (move_notation, weight, opening_name),
    ...
]
```

**Why this format?**
- **FEN keys**: Standard chess position notation enables precise position matching
- **Move tuples**: Each contains move, probability weight, and descriptive name
- **Weighted selection**: Allows variety while favoring stronger moves
- **Opening names**: Provides educational context

## Key Methods

### Initialization and Data Loading

**`__init__(book_file=None)`**
- Creates opening book from file or initializes defaults
- Sets maximum opening depth
- Calls appropriate initialization method
- **Why**: Flexible initialization supporting both file-based and default books

**`initialize_default_book()`**
- Creates comprehensive opening database with popular lines
- Covers major opening systems:
  - King's Pawn openings (1.e4)
  - Queen's Pawn openings (1.d4) 
  - Flank openings (1.Nf3, 1.c4)
- **Why**: Provides strong opening play without external files

### FEN Conversion and Position Recognition

**`get_fen_from_board(board, white_to_move, castle_rights, en_passant)`**
- Converts internal board representation to FEN notation
- Handles piece placement, turn, castling rights, en passant
- **Process**:
  1. Converts 8x8 board to FEN rank notation
  2. Adds active color (w/b)
  3. Encodes castling availability (KQkq)
  4. Sets en passant target square
- **Why**: FEN is chess standard for position representation

**Piece Notation Conversion**:
- Internal: "wK" (white king), "bp" (black pawn)
- FEN: "K" (white king), "p" (black pawn)
- **Why**: FEN uses case to distinguish colors (uppercase=white, lowercase=black)

### Move Selection Logic

**`get_book_move(board, white_to_move, castle_rights, en_passant, move_history)`**
- Main interface for getting opening book moves
- **Process**:
  1. Check if still in opening phase (move count)
  2. Convert position to FEN
  3. Look up FEN in opening database
  4. Select move using weighted random selection
  5. Convert algebraic notation to coordinates
- **Returns**: Tuple of (from_pos, to_pos, opening_name) or None
- **Why**: Provides natural interface hiding complex lookup logic

### Move Notation Handling

**`algebraic_to_move(move_str)`**
- Converts algebraic notation (e.g., "e2e4") to coordinate tuples
- **Process**:
  1. Extract source file and rank (e2)
  2. Extract destination file and rank (e4)
  3. Convert to array indices (6,4) to (4,4)
- **Why**: Bridges gap between chess notation and internal representation

### File Operations

**`save_to_file(filename)`**
- Serializes opening book to JSON format
- Saves both book data and configuration
- **Why**: Enables custom opening books and data persistence

**`load_from_file(filename)`**
- Loads opening book from JSON file
- Handles missing files gracefully
- Falls back to default book on errors
- **Why**: Supports customizable opening databases

## Opening Database Content

### Major Opening Systems Included

#### King's Pawn Game (1.e4)
- **Open Game**: 1.e4 e5 (classical central control)
- **Sicilian Defense**: 1.e4 c5 (asymmetrical, complex)
- **French Defense**: 1.e4 e6 (solid, strategic)
- **Caro-Kann Defense**: 1.e4 c6 (reliable, less tactical)

#### Queen's Pawn Game (1.d4)
- **Queen's Gambit**: 1.d4 d5 2.c4 (classical opening)
- **Indian Defenses**: 1.d4 Nf6 (hypermodern approach)
- **Dutch Defense**: 1.d4 f5 (aggressive, unbalanced)

#### Flank Openings
- **English Opening**: 1.c4 (flexible, transpositional)
- **Reti Opening**: 1.Nf3 (hypermodern development)

### Specific Variations

#### Ruy Lopez (Spanish Opening)
```python
"r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq -": [
    ("a7a6", 60, "Morphy Defense"),    # Most popular
    ("g8f6", 20, "Berlin Defense"),    # Modern, solid
    ("f7f5", 10, "Schliemann Defense"), # Aggressive
    ("f8c5", 10, "Classical Defense")   # Traditional
]
```

#### Sicilian Defense
```python
"rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq -": [
    ("d7d6", 35, "Dragon/Najdorf setup"),
    ("b8c6", 30, "Classical Sicilian"),
    ("e7e6", 25, "Taimanov/Paulsen"),
    ("g7g6", 10, "Hyperaccelerated Dragon")
]
```

## Weighted Move Selection Algorithm

### Selection Process
1. Calculate total weight of all moves in position
2. Generate random number between 0 and total weight
3. Iterate through moves, subtracting weights
4. Return move when random number reached
5. **Why**: Provides variety while favoring stronger moves

### Weight Interpretation
- **High weights (60-90)**: Main theoretical moves
- **Medium weights (20-40)**: Reasonable alternatives
- **Low weights (5-15)**: Playable but less common
- **Why**: Balances strength with variety for interesting games

## Integration with AI System

### Usage Pattern
```python
if opening_book_available:
    book_move = opening_book.get_book_move(...)
    if book_move:
        return book_move  # Use book move
    
# Fall back to calculation
return search_engine.find_best_move(...)
```

### Performance Benefits
- **Speed**: Instant move vs. 5+ second calculation
- **Quality**: Centuries of theory vs. limited search depth
- **Consistency**: Plays established systems vs. random early moves

## Educational Aspects

### Opening Principles Demonstrated
- **Central Control**: e4, d4 opening moves
- **Rapid Development**: Knights before bishops
- **King Safety**: Early castling in many lines
- **Pawn Structure**: Sound pawn formations

### Named Openings
Each move includes opening name for educational context:
- "Italian Game"
- "Queen's Gambit Declined"
- "Nimzo-Indian Defense"
- "Sicilian Dragon"

## Limitations and Considerations

### Database Size
- Current: ~50 positions covering 12 moves deep
- Could be expanded to thousands of positions
- **Trade-off**: Memory usage vs. opening coverage

### Move Selection
- Weighted random provides variety but isn't deterministic
- Strong players might prefer most popular moves always
- **Design choice**: Education and variety over pure strength

### Maintenance
- Opening theory evolves over time
- New discoveries could make some lines obsolete
- **Solution**: Updateable database format

## Future Enhancements

### Possible Improvements
- **Larger Database**: Professional opening books with thousands of positions
- **Move Annotations**: Comments explaining opening ideas
- **Transposition Handling**: Multiple move orders reaching same position
- **Player Style**: Different opening preferences for variety
- **Learning**: Track which openings lead to better results

### Integration Options
- **PGN Import**: Load openings from professional game databases
- **Online Updates**: Download latest opening theory
- **Custom Books**: Player-specific opening repertoires

The OpeningBook provides a solid foundation for strong early-game play while maintaining educational value and code simplicity.