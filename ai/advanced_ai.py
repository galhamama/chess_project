from __future__ import annotations
import random
import time
import os
import threading
from dataclasses import dataclass
from collections import defaultdict
from typing import TYPE_CHECKING, Optional, Tuple, List, Dict, NamedTuple
from enum import Enum

if TYPE_CHECKING:
    from core.game_state import GameState
    from core.move import Move

try:
    from .opening_book import OpeningBook  
    OPENING_BOOK_AVAILABLE = True
except ImportError:
    OPENING_BOOK_AVAILABLE = False
    print("Opening book module not found. AI will calculate all moves.")

# Configuration and Constants
@dataclass
class AIConfig:
    """AI configuration parameters"""
    max_depth: int = 6
    time_limit: float = 5.0
    tt_size_mb: int = 64
    use_opening_book: bool = True
    use_null_move_pruning: bool = True
    use_lmr: bool = True
    use_killer_moves: bool = True
    
    # Evaluation weights
    piece_values: Dict[str, int] = None
    
    def __post_init__(self):
        if self.piece_values is None:
            self.piece_values = {"K": 0, "Q": 900, "R": 500, "B": 330, "N": 320, "p": 100}

class MoveType(Enum):
    ALL = "all"
    CAPTURES = "captures"
    QUIET = "quiet"

class Move(NamedTuple):
    """Lightweight move representation"""
    from_row: int
    from_col: int
    to_row: int  
    to_col: int
    piece: str = ""
    captured: str = ""
    special_flag: str = ""  # promotion, castle, en_passant

class TranspositionEntry(NamedTuple):
    """Transposition table entry"""
    score: int
    depth: int
    flag: int  # EXACT, LOWER_BOUND, UPPER_BOUND
    best_move: Optional[Move]
    age: int

class TranspositionTable:
    """High-performance transposition table"""
    
    EXACT = 0
    LOWER_BOUND = 1
    UPPER_BOUND = 2
    
    def __init__(self, size_mb: int = 64):
        self.size = (size_mb * 1024 * 1024) // 32  # ~32 bytes per entry
        self.table: Dict[int, TranspositionEntry] = {}
        self.generation = 0
        self.hits = 0
        self.misses = 0

    def clear(self):
        self.table.clear()
        self.generation = 0
        self.hits = 0
        self.misses = 0
    
    def new_search(self):
        self.generation += 1
    
    def store(self, key: int, depth: int, score: int, flag: int, best_move: Optional[Move] = None):
        if key in self.table:
            old_entry = self.table[key]
            # Replace if deeper or newer
            if depth >= old_entry.depth or abs(self.generation - old_entry.age) > 2:
                self.table[key] = TranspositionEntry(score, depth, flag, best_move, self.generation)
        else:
            if len(self.table) < self.size:
                self.table[key] = TranspositionEntry(score, depth, flag, best_move, self.generation)
    
    def probe(self, key: int, depth: int, alpha: int, beta: int) -> Tuple[Optional[int], Optional[Move]]:
        if key not in self.table:
            self.misses += 1
            return None, None
        
        self.hits += 1
        entry = self.table[key]
        
        if entry.depth >= depth:
            if entry.flag == self.EXACT:
                return entry.score, entry.best_move
            elif entry.flag == self.LOWER_BOUND and entry.score >= beta:
                return entry.score, entry.best_move
            elif entry.flag == self.UPPER_BOUND and entry.score <= alpha:
                return entry.score, entry.best_move
        
        return None, entry.best_move
    
    def get_hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

class MoveGenerator:
    """Unified move generation system"""
    
    @staticmethod
    def is_valid_square(row: int, col: int) -> bool:
        return 0 <= row < 8 and 0 <= col < 8
    
    @staticmethod
    def generate_moves(board: List[List[str]], is_white_turn: bool, move_type: MoveType = MoveType.ALL) -> List[Move]:
        """Generate moves of specified type"""
        moves = []
        color = 'w' if is_white_turn else 'b'
        
        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if piece != "--" and piece[0] == color:
                    piece_moves = MoveGenerator._get_piece_moves(board, row, col, piece, move_type)
                    moves.extend(piece_moves)
        
        return moves
    
    @staticmethod
    def _get_piece_moves(board: List[List[str]], row: int, col: int, piece: str, move_type: MoveType) -> List[Move]:
        """Get moves for a specific piece"""
        piece_type = piece[1].lower()
        color = piece[0]
        
        if piece_type == 'p':
            return MoveGenerator._get_pawn_moves(board, row, col, color, move_type)
        elif piece_type == 'r':
            return MoveGenerator._get_sliding_moves(board, row, col, color, 
                                                  [(0,1), (0,-1), (1,0), (-1,0)], move_type)
        elif piece_type == 'n':
            return MoveGenerator._get_knight_moves(board, row, col, color, move_type)
        elif piece_type == 'b':
            return MoveGenerator._get_sliding_moves(board, row, col, color,
                                                  [(1,1), (1,-1), (-1,1), (-1,-1)], move_type)
        elif piece_type == 'q':
            return MoveGenerator._get_sliding_moves(board, row, col, color,
                                                  [(0,1), (0,-1), (1,0), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)], move_type)
        elif piece_type == 'k':
            return MoveGenerator._get_king_moves(board, row, col, color, move_type)
        
        return []
    
    @staticmethod
    def _get_pawn_moves(board: List[List[str]], row: int, col: int, color: str, move_type: MoveType) -> List[Move]:
        moves = []
        direction = -1 if color == 'w' else 1
        start_row = 6 if color == 'w' else 1
        
        # Forward moves (quiet)
        if move_type in [MoveType.ALL, MoveType.QUIET]:
            new_row = row + direction
            if MoveGenerator.is_valid_square(new_row, col) and board[new_row][col] == "--":
                moves.append(Move(row, col, new_row, col, piece=color+'p'))
                
                # Double move
                if row == start_row and board[new_row + direction][col] == "--":
                    moves.append(Move(row, col, new_row + direction, col, piece=color+'p'))
        
        # Captures
        if move_type in [MoveType.ALL, MoveType.CAPTURES]:
            for dc in [-1, 1]:
                new_row, new_col = row + direction, col + dc
                if (MoveGenerator.is_valid_square(new_row, new_col) and 
                    board[new_row][new_col] != "--" and 
                    board[new_row][new_col][0] != color):
                    moves.append(Move(row, col, new_row, new_col, piece=color+'p', 
                                    captured=board[new_row][new_col]))
        
        return moves
    
    @staticmethod
    def _get_sliding_moves(board: List[List[str]], row: int, col: int, color: str, 
                          directions: List[Tuple[int, int]], move_type: MoveType) -> List[Move]:
        moves = []
        piece = board[row][col]
        
        for dr, dc in directions:
            for i in range(1, 8):
                new_row, new_col = row + i * dr, col + i * dc
                if not MoveGenerator.is_valid_square(new_row, new_col):
                    break
                
                target = board[new_row][new_col]
                if target == "--":
                    if move_type in [MoveType.ALL, MoveType.QUIET]:
                        moves.append(Move(row, col, new_row, new_col, piece=piece))
                elif target[0] != color:
                    if move_type in [MoveType.ALL, MoveType.CAPTURES]:
                        moves.append(Move(row, col, new_row, new_col, piece=piece, captured=target))
                    break
                else:
                    break
        
        return moves
    
    @staticmethod
    def _get_knight_moves(board: List[List[str]], row: int, col: int, color: str, move_type: MoveType) -> List[Move]:
        moves = []
        piece = board[row][col]
        knight_offsets = [(-2,-1), (-2,1), (-1,-2), (-1,2), (1,-2), (1,2), (2,-1), (2,1)]
        
        for dr, dc in knight_offsets:
            new_row, new_col = row + dr, col + dc
            if MoveGenerator.is_valid_square(new_row, new_col):
                target = board[new_row][new_col]
                if target == "--":
                    if move_type in [MoveType.ALL, MoveType.QUIET]:
                        moves.append(Move(row, col, new_row, new_col, piece=piece))
                elif target[0] != color:
                    if move_type in [MoveType.ALL, MoveType.CAPTURES]:
                        moves.append(Move(row, col, new_row, new_col, piece=piece, captured=target))
        
        return moves
    
    @staticmethod
    def _get_king_moves(board: List[List[str]], row: int, col: int, color: str, move_type: MoveType) -> List[Move]:
        moves = []
        piece = board[row][col]
        king_offsets = [(0,1), (0,-1), (1,0), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]
        
        for dr, dc in king_offsets:
            new_row, new_col = row + dr, col + dc
            if MoveGenerator.is_valid_square(new_row, new_col):
                target = board[new_row][new_col]
                if target == "--":
                    if move_type in [MoveType.ALL, MoveType.QUIET]:
                        moves.append(Move(row, col, new_row, new_col, piece=piece))
                elif target[0] != color:
                    if move_type in [MoveType.ALL, MoveType.CAPTURES]:
                        moves.append(Move(row, col, new_row, new_col, piece=piece, captured=target))
        
        return moves

class BoardAnalyzer:
    """Single-pass board analysis for evaluation"""
    
    @dataclass
    class BoardInfo:
        """Complete board analysis in one pass"""
        material_balance: int = 0
        white_king_pos: Optional[Tuple[int, int]] = None
        black_king_pos: Optional[Tuple[int, int]] = None
        white_pawns: List[Tuple[int, int]] = None
        black_pawns: List[Tuple[int, int]] = None
        piece_positions: Dict[str, List[Tuple[int, int]]] = None
        
        def __post_init__(self):
            if self.white_pawns is None:
                self.white_pawns = []
            if self.black_pawns is None:
                self.black_pawns = []
            if self.piece_positions is None:
                self.piece_positions = defaultdict(list)
    
    @staticmethod
    def analyze_board(board: List[List[str]], piece_values: Dict[str, int]) -> BoardInfo:
        """Single pass board analysis"""
        info = BoardAnalyzer.BoardInfo()
        
        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if piece == "--":
                    continue
                
                color, piece_type = piece[0], piece[1]
                pos = (row, col)
                
                # Material balance
                value = piece_values.get(piece_type, 0)
                if color == 'w':
                    info.material_balance += value
                else:
                    info.material_balance -= value
                
                # Special positions
                if piece == 'wK':
                    info.white_king_pos = pos
                elif piece == 'bK':
                    info.black_king_pos = pos
                elif piece == 'wp':
                    info.white_pawns.append(pos)
                elif piece == 'bp':
                    info.black_pawns.append(pos)
                
                # All piece positions
                info.piece_positions[piece].append(pos)
        
        return info

class Evaluator:
    """Position evaluation system"""
    
    def __init__(self, config: AIConfig):
        self.config = config
        self.piece_square_tables = self._init_piece_square_tables()
    
    def _init_piece_square_tables(self) -> Dict[str, List[List[int]]]:
        """Initialize piece-square tables"""
        return {
            'p': [
                [0,   0,   0,   0,   0,   0,   0,   0],
                [50,  50,  50,  50,  50,  50,  50,  50],
                [10,  10,  20,  30,  30,  20,  10,  10],
                [5,   5,   10,  27,  27,  10,  5,   5],
                [0,   0,   0,   25,  25,  0,   0,   0],
                [5,   -5,  -10, 0,   0,   -10, -5,  5],
                [5,   10,  10,  -25, -25, 10,  10,  5],
                [0,   0,   0,   0,   0,   0,   0,   0]
            ],
            'N': [
                [-50, -40, -30, -30, -30, -30, -40, -50],
                [-40, -20, 0,   0,   0,   0,   -20, -40],
                [-30, 0,   10,  15,  15,  10,  0,   -30],
                [-30, 5,   15,  20,  20,  15,  5,   -30],
                [-30, 0,   15,  20,  20,  15,  0,   -30],
                [-30, 5,   10,  15,  15,  10,  5,   -30],
                [-40, -20, 0,   5,   5,   0,   -20, -40],
                [-50, -40, -30, -30, -30, -30, -40, -50]
            ],
            'B': [
                [-20, -10, -10, -10, -10, -10, -10, -20],
                [-10, 0,   0,   0,   0,   0,   0,   -10],
                [-10, 0,   5,   10,  10,  5,   0,   -10],
                [-10, 5,   5,   10,  10,  5,   5,   -10],
                [-10, 0,   10,  10,  10,  10,  0,   -10],
                [-10, 10,  10,  10,  10,  10,  10,  -10],
                [-10, 5,   0,   0,   0,   0,   5,   -10],
                [-20, -10, -40, -10, -10, -40, -10, -20]
            ]
        }
    
    def evaluate_position(self, board: List[List[str]], is_white_turn: bool) -> int:
        """Comprehensive position evaluation"""
        info = BoardAnalyzer.analyze_board(board, self.config.piece_values)
        
        score = 0
        score += info.material_balance
        score += self._evaluate_piece_square_bonus(info)
        score += self._evaluate_king_safety(board, info)
        score += self._evaluate_pawn_structure(board, info)
        score += self._evaluate_mobility(board, is_white_turn)
        
        return score if is_white_turn else -score
    
    def _evaluate_piece_square_bonus(self, info: BoardAnalyzer.BoardInfo) -> int:
        """Evaluate piece-square table bonuses"""
        score = 0
        
        for piece, positions in info.piece_positions.items():
            if len(positions) == 0:
                continue
                
            color, piece_type = piece[0], piece[1].lower()
            if piece_type not in self.piece_square_tables:
                continue
            
            table = self.piece_square_tables[piece_type]
            
            for row, col in positions:
                # Flip table for black pieces
                eval_row = row if color == 'w' else 7 - row
                bonus = table[eval_row][col]
                
                if color == 'w':
                    score += bonus
                else:
                    score -= bonus
        
        return score
    
    def _evaluate_king_safety(self, board: List[List[str]], info: BoardAnalyzer.BoardInfo) -> int:
        """Evaluate king safety"""
        score = 0
        
        if info.white_king_pos:
            score += self._evaluate_pawn_shield(board, info.white_king_pos, 'w')
        
        if info.black_king_pos:
            score -= self._evaluate_pawn_shield(board, info.black_king_pos, 'b')
        
        return score
    
    def _evaluate_pawn_shield(self, board: List[List[str]], king_pos: Tuple[int, int], color: str) -> int:
        """Evaluate pawn shield around king"""
        row, col = king_pos
        shield_score = 0
        direction = -1 if color == 'w' else 1
        
        for dc in [-1, 0, 1]:
            shield_col = col + dc
            if 0 <= shield_col < 8:
                shield_row = row + direction
                if 0 <= shield_row < 8:
                    piece = board[shield_row][shield_col]
                    if piece == color + 'p':
                        shield_score += 10
                    else:
                        shield_score -= 15
        
        return shield_score
    
    def _evaluate_pawn_structure(self, board: List[List[str]], info: BoardAnalyzer.BoardInfo) -> int:
        """Evaluate pawn structure"""
        score = 0
        
        # Doubled pawns penalty
        white_files = [col for row, col in info.white_pawns]
        black_files = [col for row, col in info.black_pawns]
        
        for file in range(8):
            white_count = white_files.count(file)
            black_count = black_files.count(file)
            
            if white_count > 1:
                score -= 10 * (white_count - 1)
            if black_count > 1:
                score += 10 * (black_count - 1)
        
        # Passed pawns
        for row, col in info.white_pawns:
            if self._is_passed_pawn(board, row, col, 'w'):
                score += 20 + (7 - row) * 5
        
        for row, col in info.black_pawns:
            if self._is_passed_pawn(board, row, col, 'b'):
                score -= 20 + row * 5
        
        return score
    
    def _is_passed_pawn(self, board: List[List[str]], row: int, col: int, color: str) -> bool:
        """Check if pawn is passed"""
        direction = -1 if color == 'w' else 1
        enemy_color = 'b' if color == 'w' else 'w'
        
        for check_col in [col - 1, col, col + 1]:
            if 0 <= check_col < 8:
                check_row = row + direction
                while 0 <= check_row < 8:
                    piece = board[check_row][check_col]
                    if piece == enemy_color + 'p':
                        return False
                    check_row += direction
        
        return True
    
    def _evaluate_mobility(self, board: List[List[str]], is_white_turn: bool) -> int:
        """Evaluate piece mobility"""
        white_mobility = len(MoveGenerator.generate_moves(board, True, MoveType.ALL))
        black_mobility = len(MoveGenerator.generate_moves(board, False, MoveType.ALL))
        
        return (white_mobility - black_mobility) * 2

class SearchEngine:
    """Main search engine with all optimizations"""
    
    def __init__(self, config: AIConfig):
        self.config = config
        self.tt = TranspositionTable(config.tt_size_mb)
        self.evaluator = Evaluator(config)
        
        # Search state
        self.nodes_searched = 0
        self.start_time = 0
        self.cancel_search = False
        
        # Move ordering
        self.killer_moves = defaultdict(list)  # ply -> [move1, move2]
        self.history_scores = defaultdict(int)  # (piece, to_square) -> score
        
        # Statistics
        self.stats = {
            'beta_cutoffs': 0,
            'first_move_cutoffs': 0,
            'null_move_cuts': 0,
            'lmr_saves': 0
        }
    
    def find_best_move(self, board: List[List[str]], is_white_turn: bool, valid_moves: List) -> Optional:
        """Find best move using iterative deepening"""
        self.nodes_searched = 0
        self.start_time = time.time()
        self.cancel_search = False
        
        self.tt.new_search()
        self.killer_moves.clear()
        self.history_scores.clear()
        self._reset_stats()
        
        if not valid_moves:
            return None
        
        if len(valid_moves) == 1:
            return valid_moves[0]
        
        # Convert to internal move format
        moves = self._convert_moves(board, valid_moves)
        
        best_move = None
        
        print(f"Starting search with {len(moves)} moves...")
        
        # Iterative deepening
        for depth in range(1, self.config.max_depth + 1):
            if self._should_stop_search():
                break
            
            current_best = self._search_root(board, is_white_turn, moves, depth)
            
            if not self._should_stop_search() and current_best:
                best_move = current_best
                elapsed = time.time() - self.start_time
                nps = int(self.nodes_searched / max(elapsed, 0.001))
                print(f"Depth {depth}: {nps:,} nps")
        
        self._print_search_stats()
        return self._convert_back_to_original_move(best_move, valid_moves) if best_move else random.choice(valid_moves)
    
    def _search_root(self, board: List[List[str]], is_white_turn: bool, moves: List[Move], depth: int) -> Optional[Move]:
        """Root search with move ordering"""
        best_move = None
        best_score = -999999
        
        # Order moves
        ordered_moves = self._order_moves(board, moves, 0, None)
        
        for move in ordered_moves:
            if self._should_stop_search():
                break
            
            # Make move
            new_board = self._make_move(board, move)
            
            # Search
            score = -self._alpha_beta(new_board, not is_white_turn, depth - 1, -999999, 999999, 1)
            
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move
    
    def _alpha_beta(self, board: List[List[str]], is_white_turn: bool, depth: int, 
                   alpha: int, beta: int, ply: int) -> int:
        """Alpha-beta search with all optimizations"""
        
        if self._should_stop_search():
            return 0
        
        self.nodes_searched += 1
        
        # Transposition table probe
        pos_key = self._get_position_key(board, is_white_turn)
        tt_score, tt_move = self.tt.probe(pos_key, depth, alpha, beta)
        
        if tt_score is not None and depth > 0:
            return tt_score
        
        # Terminal nodes
        if depth <= 0:
            return self._quiescence_search(board, is_white_turn, alpha, beta)
        
        # Generate moves
        moves = MoveGenerator.generate_moves(board, is_white_turn, MoveType.ALL)
        
        if not moves:
            if self._is_king_in_check(board, is_white_turn):
                return -999999 + ply  # Checkmate
            else:
                return 0  # Stalemate
        
        # Null move pruning
        if (self.config.use_null_move_pruning and depth >= 3 and 
            not self._is_king_in_check(board, is_white_turn) and 
            self._has_non_pawn_pieces(board, is_white_turn)):
            
            reduction = 3 + depth // 4
            null_score = -self._alpha_beta(board, not is_white_turn, depth - reduction - 1, 
                                         -beta, -beta + 1, ply + 1)
            
            if null_score >= beta:
                self.stats['null_move_cuts'] += 1
                return beta
        
        # Search moves
        ordered_moves = self._order_moves(board, moves, ply, tt_move)
        best_score = -999999
        moves_searched = 0
        
        for i, move in enumerate(ordered_moves):
            # Make move
            new_board = self._make_move(board, move)
            
            # Late move reductions
            reduction = 0
            if (self.config.use_lmr and i > 3 and depth > 2 and moves_searched > 0 and 
                not move.captured and not self._is_king_in_check(new_board, not is_white_turn)):
                reduction = min(depth - 1, 1 + (depth - 1) * (i - 3) // 20)
            
            # Search
            if moves_searched == 0:
                score = -self._alpha_beta(new_board, not is_white_turn, depth - 1, -beta, -alpha, ply + 1)
            else:
                score = -self._alpha_beta(new_board, not is_white_turn, depth - 1 - reduction, 
                                        -alpha - 1, -alpha, ply + 1)
                
                if score > alpha and (reduction > 0 or score < beta):
                    self.stats['lmr_saves'] += 1 if reduction > 0 else 0
                    score = -self._alpha_beta(new_board, not is_white_turn, depth - 1, -beta, -alpha, ply + 1)
            
            moves_searched += 1
            
            if score > best_score:
                best_score = score
            
            if score > alpha:
                alpha = score
                self._update_history(move, depth, True)
            
            if alpha >= beta:
                self.stats['beta_cutoffs'] += 1
                if i == 0:
                    self.stats['first_move_cutoffs'] += 1
                
                # Update killers and history
                if not move.captured and self.config.use_killer_moves:
                    self._add_killer_move(move, ply)
                
                self._update_history(move, depth, True)
                break
        
        # Store in transposition table
        tt_flag = (TranspositionTable.EXACT if best_score > -999999 and best_score < beta else
                  TranspositionTable.LOWER_BOUND if best_score >= beta else
                  TranspositionTable.UPPER_BOUND)
        
        self.tt.store(pos_key, depth, best_score, tt_flag, ordered_moves[0] if ordered_moves else None)
        
        return best_score
    
    def _quiescence_search(self, board: List[List[str]], is_white_turn: bool, alpha: int, beta: int) -> int:
        """Quiescence search"""
        self.nodes_searched += 1
        
        stand_pat = self.evaluator.evaluate_position(board, is_white_turn)
        
        if stand_pat >= beta:
            return beta
        
        if stand_pat > alpha:
            alpha = stand_pat
        
        # Search captures
        captures = MoveGenerator.generate_moves(board, is_white_turn, MoveType.CAPTURES)
        
        for capture in captures:
            new_board = self._make_move(board, capture)
            score = -self._quiescence_search(new_board, not is_white_turn, -beta, -alpha)
            
            if score >= beta:
                return beta
            
            if score > alpha:
                alpha = score
        
        return alpha
    
    def _order_moves(self, board: List[List[str]], moves: List[Move], ply: int, tt_move: Optional[Move]) -> List[Move]:
        """Order moves for optimal search"""
        scored_moves = []
        
        for move in moves:
            score = 0
            
            # 1. Hash move (highest priority)
            if tt_move and move == tt_move:
                score += 10000000
            
            # 2. Captures (MVV-LVA)
            elif move.captured:
                victim_value = self.config.piece_values.get(move.captured[1], 0)
                attacker_value = self.config.piece_values.get(move.piece[1], 0)
                score += 1000000 + victim_value * 10 - attacker_value
            
            # 3. Killer moves
            elif self.config.use_killer_moves and move in self.killer_moves[ply]:
                killer_index = self.killer_moves[ply].index(move)
                score += 900000 - killer_index * 1000
            
            # 4. History heuristic
            else:
                history_key = (move.piece, move.to_row * 8 + move.to_col)
                score += self.history_scores[history_key]
            
            scored_moves.append((score, move))
        
        # Sort by score (highest first)
        scored_moves.sort(key=lambda x: x[0], reverse=True)
        return [move for _, move in scored_moves]
    
    def _add_killer_move(self, move: Move, ply: int):
        """Add killer move at ply"""
        if move not in self.killer_moves[ply]:
            self.killer_moves[ply].insert(0, move)
            # Keep only 2 killer moves per ply
            if len(self.killer_moves[ply]) > 2:
                self.killer_moves[ply].pop()
    
    def _update_history(self, move: Move, depth: int, is_good: bool):
        """Update history heuristic"""
        history_key = (move.piece, move.to_row * 8 + move.to_col)
        bonus = depth * depth if is_good else -depth * depth
        
        # Gravity-based update to prevent saturation
        current = self.history_scores[history_key]
        self.history_scores[history_key] = current + bonus - (current * abs(bonus) // 512)
    
    def _make_move(self, board: List[List[str]], move: Move) -> List[List[str]]:
        """Make move on board copy"""
        new_board = [row[:] for row in board]  # Copy board
        
        new_board[move.to_row][move.to_col] = move.piece
        new_board[move.from_row][move.from_col] = "--"
        
        # Handle special moves
        if move.special_flag == "promotion":
            new_board[move.to_row][move.to_col] = move.piece[0] + 'Q'
        elif move.special_flag == "en_passant":
            # Remove captured pawn
            capture_row = move.to_row + (1 if move.piece[0] == 'w' else -1)
            new_board[capture_row][move.to_col] = "--"
        elif move.special_flag == "castle":
            # Move rook
            if move.to_col > move.from_col:  # Kingside
                new_board[move.from_row][5] = new_board[move.from_row][7]
                new_board[move.from_row][7] = "--"
            else:  # Queenside
                new_board[move.from_row][3] = new_board[move.from_row][0]
                new_board[move.from_row][0] = "--"
        
        return new_board
    
    def _get_position_key(self, board: List[List[str]], is_white_turn: bool) -> int:
        """Generate position hash key"""
        key = 0
        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if piece != "--":
                    key ^= hash((piece, row, col))
        
        if is_white_turn:
            key ^= 1
        
        return key & 0x7FFFFFFF
    
    def _is_king_in_check(self, board: List[List[str]], is_white_turn: bool) -> bool:
        """Check if king is in check"""
        king_piece = 'wK' if is_white_turn else 'bK'
        king_pos = None
        
        # Find king
        for row in range(8):
            for col in range(8):
                if board[row][col] == king_piece:
                    king_pos = (row, col)
                    break
        
        if not king_pos:
            return False
        
        # Check if any enemy piece attacks the king
        enemy_moves = MoveGenerator.generate_moves(board, not is_white_turn, MoveType.ALL)
        
        for move in enemy_moves:
            if move.to_row == king_pos[0] and move.to_col == king_pos[1]:
                return True
        
        return False
    
    def _has_non_pawn_pieces(self, board: List[List[str]], is_white_turn: bool) -> bool:
        """Check if side has non-pawn pieces"""
        color = 'w' if is_white_turn else 'b'
        
        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if piece != "--" and piece[0] == color and piece[1].lower() not in ['k', 'p']:
                    return True
        
        return False
    
    def _should_stop_search(self) -> bool:
        """Check if search should be stopped"""
        return (self.cancel_search or 
                (time.time() - self.start_time) > self.config.time_limit)
    
    def _convert_moves(self, board: List[List[str]], original_moves: List) -> List[Move]:
        """Convert original moves to internal format"""
        moves = []
        for move in original_moves:
            # Extract move information
            piece = board[move.start_row][move.start_col]
            captured = board[move.end_row][move.end_col] if board[move.end_row][move.end_col] != "--" else ""
            
            # Determine special flags
            special_flag = ""
            if hasattr(move, 'pawn_promotion') and move.pawn_promotion:
                special_flag = "promotion"
            elif hasattr(move, 'enPassant') and move.enPassant:
                special_flag = "en_passant"
            elif hasattr(move, 'is_castle_move') and move.is_castle_move:
                special_flag = "castle"
            
            internal_move = Move(
                move.start_row, move.start_col, move.end_row, move.end_col,
                piece, captured, special_flag
            )
            moves.append(internal_move)
        
        return moves
    
    def _convert_back_to_original_move(self, internal_move: Move, original_moves: List):
        """Convert internal move back to original format"""
        for move in original_moves:
            if (move.start_row == internal_move.from_row and 
                move.start_col == internal_move.from_col and
                move.end_row == internal_move.to_row and 
                move.end_col == internal_move.to_col):
                return move
        
        return None
    
    def _reset_stats(self):
        """Reset search statistics"""
        for key in self.stats:
            self.stats[key] = 0
    
    def _print_search_stats(self):
        """Print search statistics"""
        elapsed = time.time() - self.start_time
        nps = int(self.nodes_searched / max(elapsed, 0.001))
        
        print(f"\nSearch Statistics:")
        print(f"Nodes searched: {self.nodes_searched:,}")
        print(f"Time elapsed: {elapsed:.2f}s")
        print(f"Nodes per second: {nps:,}")
        print(f"TT hit rate: {self.tt.get_hit_rate():.1%}")
        print(f"Beta cutoffs: {self.stats['beta_cutoffs']}")
        if self.stats['beta_cutoffs'] > 0:
            print(f"First move cutoffs: {self.stats['first_move_cutoffs']} "
                  f"({self.stats['first_move_cutoffs']/self.stats['beta_cutoffs']:.1%})")
        print(f"Null move cuts: {self.stats['null_move_cuts']}")
        print(f"LMR re-searches: {self.stats['lmr_saves']}")

class AdvancedChessAI:
    """Main Chess AI interface - refactored and optimized"""
    
    def __init__(self, gs: GameState, config: Optional[AIConfig] = None):
        self.config = config or AIConfig()
        self.search_engine = SearchEngine(self.config)
        self.gs = gs
        
        # Opening book setup
        self.opening_book = None
        self.last_opening_name = None
        
        if OPENING_BOOK_AVAILABLE and self.config.use_opening_book:
            self._initialize_opening_book()
    
    def _initialize_opening_book(self):
        """Initialize opening book"""
        book_paths = [
            "data/opening_book.json",
            "../data/opening_book.json", 
            "opening_book.json"
        ]
        
        for book_path in book_paths:
            if os.path.exists(book_path):
                try:
                    self.opening_book = OpeningBook(book_path)
                    print(f"✓ Opening book loaded from {book_path}")
                    return
                except Exception as e:
                    print(f"Failed to load opening book from {book_path}: {e}")
        
        # Fallback to default book
        try:
            self.opening_book = OpeningBook()
            print("✓ Default opening book loaded")
        except Exception as e:
            print(f"Opening book initialization failed: {e}")
            self.opening_book = None
    
    def find_best_move(self, game_state: GameState, valid_moves: List, return_queue) -> Optional:
        """Main interface for finding best move"""
        self.gs = game_state
        
        # Check opening book first
        if (self.config.use_opening_book and self.opening_book and 
            OPENING_BOOK_AVAILABLE):
            
            book_move = self._try_opening_book(game_state, valid_moves)
            if book_move:
                return_queue.put(book_move)
                return book_move
        
        # Use search engine
        best_move = self.search_engine.find_best_move(
            game_state.board, game_state.white_to_move, valid_moves
        )
        
        return_queue.put(best_move)
        return best_move
    
    def _try_opening_book(self, game_state: GameState, valid_moves: List):
        """Try to get move from opening book"""
        try:
            book_result = self.opening_book.get_book_move(
                game_state.board,
                game_state.white_to_move,
                game_state.current_castling_rights,
                game_state.enPassant_possible,
                game_state.move_log
            )
            
            if book_result:
                from_pos, to_pos, opening_name = book_result
                
                # Find corresponding move
                for move in valid_moves:
                    if (move.start_row == from_pos[0] and 
                        move.start_col == from_pos[1] and
                        move.end_row == to_pos[0] and 
                        move.end_col == to_pos[1]):
                        
                        # Print opening info
                        if opening_name != self.last_opening_name:
                            print(f"\n📖 Opening: {opening_name}")
                            self.last_opening_name = opening_name
                        
                        print(f"   Book move: {move.get_chess_notation()}")
                        return move
        
        except Exception as e:
            print(f"Opening book error: {e}")
        
        return None
    
    def cancel_search_now(self):
        """Cancel current search"""
        self.search_engine.cancel_search = True
    
    def set_difficulty(self, level: int):
        """Set AI difficulty level"""
        if level == 1:  # Easy
            self.config.max_depth = 4
            self.config.time_limit = 2.0
        elif level == 2:  # Medium
            self.config.max_depth = 6
            self.config.time_limit = 5.0
        elif level == 3:  # Hard
            self.config.max_depth = 8
            self.config.time_limit = 10.0
        else:
            self.config.max_depth = 6
            self.config.time_limit = 5.0
        
        print(f"AI difficulty set: depth={self.config.max_depth}, time={self.config.time_limit}s")
    
    def find_random_move(self, valid_moves: List):
        """Fallback random move"""
        return random.choice(valid_moves) if valid_moves else None
    
    def disable_opening_book(self):
        """Disable opening book"""
        self.config.use_opening_book = False
        print("Opening book disabled")
    
    def enable_opening_book(self):
        """Enable opening book"""
        if self.opening_book and OPENING_BOOK_AVAILABLE:
            self.config.use_opening_book = True
            print("Opening book enabled")
        else:
            print("Opening book not available")
    
    def save_opening_book(self, filepath: str = "data/opening_book.json"):
        """Save opening book to file"""
        if self.opening_book:
            try:
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                self.opening_book.save_to_file(filepath)
                print(f"Opening book saved to {filepath}")
            except Exception as e:
                print(f"Failed to save opening book: {e}")
    
    def get_search_stats(self) -> Dict:
        """Get search statistics"""
        return {
            'nodes_searched': self.search_engine.nodes_searched,
            'tt_hit_rate': self.search_engine.tt.get_hit_rate(),
            'beta_cutoffs': self.search_engine.stats['beta_cutoffs'],
            'first_move_cutoffs': self.search_engine.stats['first_move_cutoffs'],
        }
    
    # Backward compatibility properties
    @property
    def tt(self):
        """Backward compatibility for transposition table access"""
        return self.search_engine.tt
    
    @property
    def nodes_searched(self):
        """Backward compatibility for nodes_searched access"""
        return self.search_engine.nodes_searched
    
    @property
    def beta_cutoffs(self):
        """Backward compatibility for beta_cutoffs access"""
        return self.search_engine.stats['beta_cutoffs']
    
    @property
    def first_move_cutoffs(self):
        """Backward compatibility for first_move_cutoffs access"""
        return self.search_engine.stats['first_move_cutoffs']
    
    def configure(self, **kwargs):
        """Configure AI parameters"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                print(f"Set {key} = {value}")
            else:
                print(f"Unknown configuration parameter: {key}")
    
    # Backward compatibility methods
    def evaluate_position(self, board: List[List[str]], is_white_turn: bool) -> int:
        """Evaluate position (for backward compatibility)"""
        return self.search_engine.evaluator.evaluate_position(board, is_white_turn)
    
    def copy_board(self, board: List[List[str]]) -> List[List[str]]:
        """Copy board (for backward compatibility)"""
        return [row[:] for row in board]