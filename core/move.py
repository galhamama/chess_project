"""Chess move representation and utilities"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .constants import CastleRights

class CastleRights:
    def __init__(self, wks: bool, bks: bool, wqs: bool, bqs: bool):
        """Castling rights for both sides"""
        self.wks = wks  # White kingside
        self.bks = bks  # Black kingside
        self.wqs = wqs  # White queenside
        self.bqs = bqs  # Black queenside
    
    def __eq__(self, other):
        """Equality comparison for castle rights"""
        if not isinstance(other, CastleRights):
            return False
        return (self.wks == other.wks and self.bks == other.bks and 
                self.wqs == other.wqs and self.bqs == other.bqs)
    
    def copy(self):
        """Create a copy of castle rights"""
        return CastleRights(self.wks, self.bks, self.wqs, self.bqs)


class Move:
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_sq: tuple[int, int], end_sq: tuple[int, int], 
                 board: list[list[str]], enPassant: bool = False, 
                 pawn_promotion: bool = False, is_castle_move: bool = False):
        """Enhanced Move class with complete undo information"""
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.enPassant = enPassant
        self.pawn_promotion = pawn_promotion
        self.is_castle_move = is_castle_move
        
        # Store complete move information for proper undo
        self.promoted_to = None
        self.last_moved = 0
        
        # Handle en passant captured piece
        if self.enPassant:
            self.piece_captured = 'bp' if self.piece_moved == 'wp' else 'wp'
        
        # Store additional state for undo
        self.castle_rights_before = None
        self.en_passant_before = None
        self.fifty_move_counter = 0
        
        # Move identification
        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col
        self.special_id = self.get_special_id()

    def get_special_id(self):
        """Create unique identifier including special move types"""
        special_id = 0
        if self.piece_moved != "--":
            special_id += ord(self.piece_moved[0]) + ord(self.piece_moved[1])
        if self.enPassant:
            special_id += 3
        if self.pawn_promotion:
            special_id += 7
        if self.is_castle_move:
            special_id += 9
        special_id += ord(self.piece_captured[0]) + ord(self.piece_captured[1])
        return special_id

    def set_promotion_piece(self, piece: str):
        """Set what piece the pawn promotes to"""
        self.promoted_to = piece

    def set_castle_rights_before(self, castle_rights):
        """Store castle rights before the move for undo"""
        self.castle_rights_before = castle_rights.copy() if castle_rights else None

    def set_en_passant_before(self, en_passant_square):
        """Store en passant state before the move"""
        self.en_passant_before = en_passant_square

    def set_last_moved(self, turn: int):
        """Set when this piece last moved"""
        self.last_moved = turn

    def __eq__(self, other) -> bool:
        """Enhanced equality comparison"""
        if not isinstance(other, Move):
            return False
        return (self.start_row == other.start_row and self.start_col == other.start_col and
                self.end_row == other.end_row and self.end_col == other.end_col and
                self.piece_moved == other.piece_moved and self.pawn_promotion == other.pawn_promotion and
                self.enPassant == other.enPassant and self.is_castle_move == other.is_castle_move)

    def __hash__(self) -> int:
        """Hash for use in sets and dictionaries"""
        return hash((self.start_row, self.start_col, self.end_row, self.end_col, 
                    self.piece_moved, self.piece_captured, self.enPassant, 
                    self.pawn_promotion, self.is_castle_move))
        
    def get_chess_notation(self) -> str:
        """Get algebraic notation for the move"""
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)
    
    def get_rank_file(self, r: int, c: int) -> str:
        """Convert row/col to chess notation"""
        return self.cols_to_files[c] + self.rows_to_ranks[r]

    def is_valid(self) -> bool:
        """Check if move coordinates are valid"""
        return (0 <= self.start_row < 8 and 0 <= self.start_col < 8 and
                0 <= self.end_row < 8 and 0 <= self.end_col < 8 and
                self.piece_moved != "--")

    def __str__(self) -> str:
        """String representation for debugging"""
        return f"Move({self.get_chess_notation()}: {self.piece_moved} -> {self.piece_captured if self.piece_captured != '--' else 'empty'})"

    def __repr__(self) -> str:
        """Detailed representation for debugging"""
        return (f"Move({self.start_row},{self.start_col}->{self.end_row},{self.end_col}, "
                f"piece={self.piece_moved}, captured={self.piece_captured}, "
                f"promotion={self.pawn_promotion}, castle={self.is_castle_move}, "
                f"enpassant={self.enPassant})")
