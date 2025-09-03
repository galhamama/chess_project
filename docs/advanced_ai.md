# ai/advanced_ai.py - Chess AI Engine

## Purpose
This module implements a sophisticated chess AI engine using advanced algorithms including alpha-beta pruning, iterative deepening, transposition tables, and various search optimizations. It represents the core artificial intelligence that provides challenging computer opponents.

## Architecture Overview
The AI is built using several interconnected classes that work together to analyze chess positions and find the best moves:

1. **AdvancedChessAI**: Main interface and coordinator
2. **SearchEngine**: Core search algorithms and move evaluation
3. **Evaluator**: Position evaluation and scoring
4. **TranspositionTable**: Position caching for performance
5. **MoveGenerator**: Efficient move generation
6. **BoardAnalyzer**: Single-pass board analysis

## Key Classes and Components

### AIConfig (Dataclass)
**Purpose**: Centralized configuration for AI behavior and parameters.

#### Variables
- `max_depth`: Maximum search depth (default: 6)
- `time_limit`: Maximum thinking time in seconds (default: 5.0)
- `tt_size_mb`: Transposition table size in megabytes (default: 64)
- `use_opening_book`: Enable/disable opening book (default: True)
- `use_null_move_pruning`: Enable null move optimization (default: True)
- `use_lmr`: Enable late move reductions (default: True)
- `use_killer_moves`: Enable killer move heuristic (default: True)
- `piece_values`: Dictionary of piece values for evaluation

**Why this design**: Centralizes all AI parameters, making it easy to configure different difficulty levels and experiment with settings.

### TranspositionTable Class
**Purpose**: High-performance caching system for previously evaluated positions.

#### Key Variables
- `table`: Dictionary storing position evaluations
- `generation`: Current search generation counter
- `hits/misses`: Performance statistics
- `size`: Maximum number of entries

#### Key Methods
**`store(key, depth, score, flag, best_move)`**
- Stores position evaluation with replacement strategy
- Uses depth and age for replacement decisions
- Why: Prevents table overflow while keeping most valuable entries

**`probe(key, depth, alpha, beta)`**
- Retrieves cached evaluation if applicable
- Returns score and best move if usable
- Handles different bound types (exact, lower, upper)
- Why: Massive search speedup by avoiding re-evaluation

### MoveGenerator Class
**Purpose**: Efficient generation of chess moves with different filtering options.

#### Key Methods
**`generate_moves(board, is_white_turn, move_type)`**
- Generates moves of specified type (ALL, CAPTURES, QUIET)
- Unified interface for all piece types
- Why: Allows selective move generation for different search phases

**Piece-specific generators**: `_get_pawn_moves`, `_get_sliding_moves`, etc.
- Optimized algorithms for each piece type
- Handle special rules (en passant, castling)
- Why: Efficient move generation is critical for search performance

### BoardAnalyzer Class
**Purpose**: Single-pass analysis of board positions for evaluation.

#### BoardInfo (Dataclass)
- `material_balance`: Material advantage calculation
- `king_positions`: Cached king locations
- `pawn_structures`: Pawn position lists
- `piece_positions`: All piece locations by type

**`analyze_board(board, piece_values)`**
- Analyzes entire position in one board scan
- Returns comprehensive BoardInfo object
- Why: Single-pass analysis is much faster than multiple scans

### Evaluator Class
**Purpose**: Sophisticated position evaluation considering multiple chess factors.

#### Evaluation Components
**`evaluate_position(board, is_white_turn)`**
- Master evaluation function combining all factors
- Returns centipawn score from current player's perspective

**`_evaluate_piece_square_bonus(info)`**
- Uses piece-square tables for positional evaluation
- Different bonuses for pieces on different squares
- Why: Pieces are stronger in center, weaker on edges

**`_evaluate_king_safety(board, info)`**
- Evaluates king safety through pawn shield analysis
- Penalties for exposed kings
- Why: King safety is crucial in chess evaluation

**`_evaluate_pawn_structure(board, info)`**
- Analyzes pawn weaknesses and strengths
- Detects doubled pawns, passed pawns
- Why: Pawn structure determines long-term position strength

**`_evaluate_mobility(board, is_white_turn)`**
- Counts available moves for both sides
- More mobility generally indicates better position
- Why: Piece activity and options are important factors

### SearchEngine Class
**Purpose**: Core search algorithms with all optimizations.

#### Key Variables
- `nodes_searched`: Performance counter
- `start_time`: Search timing
- `cancel_search`: Early termination flag
- `killer_moves`: Best moves at each depth level
- `history_scores`: Move ordering heuristic scores

#### Core Search Methods

**`find_best_move(board, is_white_turn, valid_moves)`**
- Main entry point using iterative deepening
- Searches progressively deeper until time limit
- Returns best move found
- Why: Iterative deepening provides anytime algorithm behavior

**`_alpha_beta(board, is_white_turn, depth, alpha, beta, ply)`**
- Core alpha-beta search with all optimizations
- Implements minimax with alpha-beta pruning
- Includes null move pruning, late move reductions
- Why: Alpha-beta dramatically reduces search tree size

**`_quiescence_search(board, is_white_turn, alpha, beta)`**
- Extends search for tactical sequences
- Only considers captures to avoid horizon effect
- Why: Prevents AI from walking into tactics

#### Search Optimizations

**Null Move Pruning**
- Assumes opponent's best response to "doing nothing"
- If still better than beta, position is too good
- Why: Eliminates clearly winning positions early

**Late Move Reductions (LMR)**
- Searches later moves at reduced depth
- Re-searches if they prove better than expected
- Why: Most moves are not best, so search them less

**Move Ordering**
- Hash moves first (from transposition table)
- Captures ordered by value (MVV-LVA)
- Killer moves and history heuristic
- Why: Better move ordering improves alpha-beta efficiency

### AdvancedChessAI Class (Main Interface)
**Purpose**: Main AI interface coordinating all components.

#### Key Methods

**`find_best_move(game_state, valid_moves, return_queue)`**
- Primary interface for move selection
- Checks opening book first, then uses search
- Puts result in queue for thread communication
- Why: Clean interface hiding complex internal operations

**`set_difficulty(level)`**
- Adjusts search parameters for different skill levels
- Easy: depth 4, 2 seconds
- Medium: depth 6, 5 seconds  
- Hard: depth 8, 10 seconds
- Why: Provides adjustable challenge levels

**`cancel_search_now()`**
- Immediately stops ongoing search
- Used for move undo and game reset
- Why: Responsive user interface during AI calculations

## Advanced Algorithms Explained

### Alpha-Beta Pruning
- Eliminates branches that cannot improve the result
- Maintains alpha (best for maximizer) and beta (best for minimizer)
- Prunes when alpha >= beta
- Reduces search tree from O(b^d) to O(b^(d/2))

### Iterative Deepening
- Searches depth 1, then 2, then 3, etc.
- Stops when time limit reached
- Reuses information from previous iterations
- Provides best move even if search interrupted

### Transposition Table
- Stores previously evaluated positions
- Uses Zobrist hashing for position keys
- Handles different bound types (exact, alpha, beta cutoffs)
- Massive speedup for repeated positions

### Move Ordering Strategies
1. **Hash Move**: Best move from previous search
2. **MVV-LVA**: Most Valuable Victim, Least Valuable Attacker
3. **Killer Moves**: Moves that caused beta cutoffs
4. **History Heuristic**: Moves that were good in similar positions

## Performance Characteristics
- **Search Speed**: 50,000+ nodes/second (hardware dependent)
- **Tactical Depth**: Finds tactics 8-10 moves deep
- **Opening Knowledge**: 500+ opening positions
- **Memory Usage**: 64MB transposition table + minimal overhead
- **Response Time**: Configurable 2-10 seconds per move

## Design Patterns Used

### Strategy Pattern
Different evaluation components can be swapped or configured.

### Template Method Pattern
Search algorithms follow consistent patterns with customizable parts.

### Command Pattern
Moves are objects that can be executed and undone.

### Observer Pattern
Search statistics are collected and reported.

## Integration with Game System
- **Threading**: Runs in separate thread to avoid UI blocking
- **Cancellation**: Can be stopped immediately for responsive interface
- **Queue Communication**: Thread-safe result passing
- **Error Handling**: Graceful fallback to random moves

## Estimated Strength
The AI plays at approximately 1600-1800 ELO strength depending on time controls and hardware, suitable for intermediate players while remaining educational for beginners.

This implementation demonstrates advanced computer chess programming techniques while remaining readable and maintainable.