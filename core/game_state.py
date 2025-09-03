"""Core chess game state management"""

from __future__ import annotations
from typing import Callable, List, Tuple
from .constants import ConstantValues
from .move import Move, CastleRights

class GameState:
    def __init__(self):
        """Initialize chess game state with proper move/undo handling"""
        self.const = ConstantValues()
        
        # Initial chess board setup
        self.board: List[List[str]] = [
            ["bR","bN","bB","bQ","bK","bB","bN","bR"],
            ["bp","bp","bp","bp","bp","bp","bp","bp"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["wp","wp","wp","wp","wp","wp","wp","wp"],
            ["wR","wN","wB","wQ","wK","wB","wN","wR"]
        ]
        
        # Move generation functions
        self.move_functions: dict[str, Callable] = {
            'p': self.get_pawn_move, 'R': self.get_rook_move, 'N': self.get_knight_move,
            'B': self.get_bishop_move, 'Q': self.get_queen_move, 'K': self.get_king_move
        }
        
        # Game state variables
        self.white_to_move: bool = True
        self.move_log: List[Move] = []
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.enPassant_possible: Tuple[int, int] = ()
        self.enPassant_possible_log: List[Tuple[int, int]] = [self.enPassant_possible]
        self.current_castling_rights: CastleRights = CastleRights(True, True, True, True)
        self.castle_rights_log: List[CastleRights] = [self.current_castling_rights.copy()]
        
        # Search state for move generation
        self.pins: List[Tuple[int, int]] = []
        self.checks: List[Tuple[int, int]] = []
        self.sq_selected: Tuple[int, int] = ()
        self.player_clicks: List[Tuple[int, int]] = []
        
        # Promotion handling
        self.promotion_piece: str = "Q"
        self.ai_promotion_piece: str = "Q"
        self.player_promote: bool = False
        
        # Game status
        self.move_made: bool = False
        self.animate_move: bool = False
        self.game_over: bool = False
        self.in_check: bool = False
        self.checkmate: bool = False
        self.stalemate: bool = False
        self.turn_num = 0
        
        # Performance optimization
        self.hash_board = tuple(tuple(row) for row in self.board)

    def make_move(self, move: Move):
        """Complete move handling with proper undo information"""
        # Store state for undo BEFORE making changes
        move.set_castle_rights_before(self.current_castling_rights)
        move.set_en_passant_before(self.enPassant_possible)
        
        # Make the basic move
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.board[move.start_row][move.start_col] = self.const.EMPTY_POSITION
        
        # Add to move log
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move
        
        # Handle special moves
        self.handle_king_move(move)
        self.handle_en_passant(move)
        self.handle_pawn_promotion(move)
        self.handle_castling(move)
        
        # Update game state
        self.update_castle_rights(move)
        self.castle_rights_log.append(self.current_castling_rights.copy())
        self.enPassant_possible_log.append(self.enPassant_possible)
        
        # Update hash for performance
        self.hash_board = tuple(tuple(row) for row in self.board)

    def handle_king_move(self, move: Move):
        """Update king positions"""
        if move.piece_moved == 'wK':
            self.white_king_location = (move.end_row, move.end_col)
        elif move.piece_moved == 'bK':
            self.black_king_location = (move.end_row, move.end_col)

    def handle_en_passant(self, move: Move):
        """Handle en passant moves and setup"""
        # Check if this move creates en passant opportunity
        if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:
            self.enPassant_possible = ((move.end_row + move.start_row)//2, move.end_col)
        else:
            self.enPassant_possible = ()
        
        # Handle en passant capture
        if move.enPassant:
            # Remove the captured pawn
            if move.piece_moved[0] == 'w':  # White captures black pawn
                captured_pawn_row = move.end_row + 1
            else:  # Black captures white pawn
                captured_pawn_row = move.end_row - 1
            
            self.board[captured_pawn_row][move.end_col] = self.const.EMPTY_POSITION

    def handle_pawn_promotion(self, move: Move):
        """Handle pawn promotion with complete undo info"""
        if move.pawn_promotion:
            if self.player_promote:
                promoted_piece = self.promotion_piece
            else:
                promoted_piece = self.ai_promotion_piece
            
            # Store what we promoted to
            move.set_promotion_piece(promoted_piece)
            
            # Make the promotion
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + promoted_piece
            self.player_promote = False

    def handle_castling(self, move: Move):
        """Handle castling moves"""
        if move.is_castle_move:
            if move.end_col - move.start_col == 2:  # Kingside
                # Move rook from h-file to f-file
                rook = self.board[move.end_row][move.end_col + 1]
                self.board[move.end_row][move.end_col - 1] = rook
                self.board[move.end_row][move.end_col + 1] = self.const.EMPTY_POSITION
            else:  # Queenside
                # Move rook from a-file to d-file
                rook = self.board[move.end_row][move.end_col - 2]
                self.board[move.end_row][move.end_col + 1] = rook
                self.board[move.end_row][move.end_col - 2] = self.const.EMPTY_POSITION

    def undo_move(self):
        """Complete undo handling using stored move information"""
        if len(self.move_log) == 0:
            return False
        
        move = self.move_log.pop()
        
        # Restore basic move
        self.board[move.start_row][move.start_col] = move.piece_moved
        
        # Handle promotion undo properly
        if move.pawn_promotion:
            # The end square gets whatever was captured (or empty)
            self.board[move.end_row][move.end_col] = move.piece_captured
        else:
            # Normal move: restore captured piece
            self.board[move.end_row][move.end_col] = move.piece_captured
        
        # Restore game state
        self.white_to_move = not self.white_to_move
        
        # Undo special moves
        self.undo_king_move(move)
        self.undo_en_passant(move)
        self.undo_castling(move)
        
        # Restore state from stored information
        if move.castle_rights_before:
            self.current_castling_rights = move.castle_rights_before
        else:
            # Fallback: pop from log
            if len(self.castle_rights_log) > 1:
                self.castle_rights_log.pop()
                self.current_castling_rights = self.castle_rights_log[-1]
        
        # Restore en passant
        if hasattr(move, 'en_passant_before'):
            self.enPassant_possible = move.en_passant_before
        else:
            # Fallback: pop from log
            if len(self.enPassant_possible_log) > 1:
                self.enPassant_possible_log.pop()
                self.enPassant_possible = self.enPassant_possible_log[-1]
        
        # Clear endgame flags
        self.checkmate = False
        self.stalemate = False
        
        # Update hash
        self.hash_board = tuple(tuple(row) for row in self.board)
        
        return True

    def undo_king_move(self, move: Move):
        """Restore king positions"""
        if move.piece_moved == 'wK':
            self.white_king_location = (move.start_row, move.start_col)
        elif move.piece_moved == 'bK':
            self.black_king_location = (move.start_row, move.start_col)

    def undo_en_passant(self, move: Move):
        """Undo en passant capture"""
        if move.enPassant:
            # Restore the captured pawn
            if move.piece_moved[0] == 'w':  # White captured black pawn
                captured_pawn_row = move.end_row + 1
                captured_pawn = 'bp'
            else:  # Black captured white pawn
                captured_pawn_row = move.end_row - 1
                captured_pawn = 'wp'
            
            # Put the pawn back
            self.board[captured_pawn_row][move.end_col] = captured_pawn

    def undo_castling(self, move: Move):
        """Undo castling moves"""
        if move.is_castle_move:
            if move.end_col - move.start_col == 2:  # Kingside
                # Move rook back from f-file to h-file
                rook = self.board[move.end_row][move.end_col - 1]
                self.board[move.end_row][move.end_col + 1] = rook
                self.board[move.end_row][move.end_col - 1] = self.const.EMPTY_POSITION
            else:  # Queenside
                # Move rook back from d-file to a-file
                rook = self.board[move.end_row][move.end_col + 1]
                self.board[move.end_row][move.end_col - 2] = rook
                self.board[move.end_row][move.end_col + 1] = self.const.EMPTY_POSITION

    def update_castle_rights(self, move: Move):
        """Update castling rights based on move"""
        # King moves
        if move.piece_moved == 'wK':
            self.current_castling_rights.wqs = False
            self.current_castling_rights.wks = False
        elif move.piece_moved == 'bK':
            self.current_castling_rights.bqs = False
            self.current_castling_rights.bks = False
        
        # Rook moves
        elif move.piece_moved == 'wR':
            if move.start_row == 7:
                if move.start_col == 0:  # Queenside rook
                    self.current_castling_rights.wqs = False
                elif move.start_col == 7:  # Kingside rook
                    self.current_castling_rights.wks = False
        elif move.piece_moved == 'bR':
            if move.start_row == 0:
                if move.start_col == 0:  # Queenside rook
                    self.current_castling_rights.bqs = False
                elif move.start_col == 7:  # Kingside rook
                    self.current_castling_rights.bks = False
        
        # Rook captures
        if move.piece_captured == "wR":
            if move.end_col == 0 and move.end_row == 7:
                self.current_castling_rights.wqs = False
            elif move.end_col == 7 and move.end_row == 7:
                self.current_castling_rights.wks = False
        elif move.piece_captured == "bR":
            if move.end_col == 0 and move.end_row == 0:
                self.current_castling_rights.bqs = False
            elif move.end_col == 7 and move.end_row == 0:
                self.current_castling_rights.bks = False

    def get_valid_moves(self) -> List[Move]:
        """Get all legal moves for current position"""
        moves: List[Move] = []
        self.in_check, self.pins, self.checks = self.check_for_pins_and_checks()

        if self.white_to_move:
            king_row, king_col = self.white_king_location
        else:
            king_row, king_col = self.black_king_location

        if self.in_check:
            if len(self.checks) == 1:  # Only one check - can block or capture
                moves = self.get_all_possible_moves()
                check = self.checks[0]
                check_row, check_col = check[0], check[1]
                piece_checking = self.board[check_row][check_col]
                valid_squares = []
                
                if piece_checking[1] == 'N':  # Knight check - must capture knight
                    valid_squares = [(check_row, check_col)]
                else:
                    # Can block between king and checking piece
                    for i in range(1, 8):
                        valid_square = (king_row + check[2] * i, king_col + check[3] * i)
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[1] == check_col:
                            break
                
                # Remove moves that don't address the check
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].piece_moved[1] != 'K':
                        if not (moves[i].end_row, moves[i].end_col) in valid_squares:
                            moves.remove(moves[i])
            else:  # Double check - only king moves
                self.get_king_move(king_row, king_col, moves)
        else:
            moves = self.get_all_possible_moves()

        # Add castling moves
        if not self.in_check:
            self.get_castle_moves(king_row, king_col, moves)

        # Check for checkmate/stalemate
        if len(moves) == 0:
            if self.in_check:
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        return moves

    def get_all_possible_moves(self) -> List[Move]:
        """Generate all possible moves for current player"""
        moves = []
        for row in range(8):
            for col in range(8):
                turn = self.board[row][col][0]
                if ((turn == self.const.WHITE_PLAYER and self.white_to_move) or 
                    (turn == self.const.BLACK_PLAYER and not self.white_to_move)):
                    piece = self.board[row][col][1]
                    if piece in self.move_functions:
                        self.move_functions[piece](row, col, moves)
        return moves

    # Move generation methods (keeping your original implementations)
    def get_pawn_move(self, r: int, c: int, moves: List[Move]):
        """Generate pawn moves"""
        piece_pinned = False
        pin_direction = ()
        
        # Check for pins
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        
        if self.white_to_move:
            move_amount = -1
            start_row = 6
            back_row = 0
            enemy_color = self.const.BLACK_PLAYER
        else:
            move_amount = 1
            start_row = 1
            back_row = 7
            enemy_color = self.const.WHITE_PLAYER
        
        pawn_promotion = False
        
        # Forward moves
        if self.board[r + move_amount][c] == self.const.EMPTY_POSITION:
            if not piece_pinned or pin_direction == (move_amount, 0):
                if r + move_amount == back_row:
                    pawn_promotion = True
                moves.append(Move((r, c), (r + move_amount, c), self.board, pawn_promotion=pawn_promotion))
                if r == start_row and self.board[r + 2 * move_amount][c] == self.const.EMPTY_POSITION:
                    moves.append(Move((r, c), (r + 2 * move_amount, c), self.board))
        
        # Captures
        if c - 1 >= 0:
            if not piece_pinned or pin_direction == (move_amount, -1):
                if self.board[r + move_amount][c - 1][0] == enemy_color:
                    if r + move_amount == back_row:
                        pawn_promotion = True
                    moves.append(Move((r, c), (r + move_amount, c - 1), self.board, pawn_promotion=pawn_promotion))
                if (r + move_amount, c - 1) == self.enPassant_possible:
                    moves.append(Move((r, c), (r + move_amount, c - 1), self.board, enPassant=True))
        
        if c + 1 <= 7:
            if not piece_pinned or pin_direction == (move_amount, 1):
                if self.board[r + move_amount][c + 1][0] == enemy_color:
                    if r + move_amount == back_row:
                        pawn_promotion = True
                    moves.append(Move((r, c), (r + move_amount, c + 1), self.board, pawn_promotion=pawn_promotion))
                if (r + move_amount, c + 1) == self.enPassant_possible:
                    moves.append(Move((r, c), (r + move_amount, c + 1), self.board, enPassant=True))

    def get_rook_move(self, r: int, c: int, moves: List[Move]):
        """Generate rook moves"""
        self.get_sliding_moves(r, c, moves, [(-1, 0), (0, -1), (1, 0), (0, 1)])

    def get_bishop_move(self, r: int, c: int, moves: List[Move]):
        """Generate bishop moves"""
        self.get_sliding_moves(r, c, moves, [(-1, -1), (-1, 1), (1, -1), (1, 1)])

    def get_queen_move(self, r: int, c: int, moves: List[Move]):
        """Generate queen moves"""
        directions = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        self.get_sliding_moves(r, c, moves, directions)

    def get_sliding_moves(self, r: int, c: int, moves: List[Move], directions):
        """Generate moves for sliding pieces"""
        piece_pinned = False
        pin_direction = ()
        
        # Check for pins
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q':
                    self.pins.remove(self.pins[i])
                break
        
        enemy_color = self.const.BLACK_PLAYER if self.white_to_move else self.const.WHITE_PLAYER
        
        for direction in directions:
            for i in range(1, 8):
                end_row = r + direction[0] * i
                end_col = c + direction[1] * i
                
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    if not piece_pinned or pin_direction == direction or pin_direction == (-direction[0], -direction[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == self.const.EMPTY_POSITION:
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color:
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                            break
                        else:
                            break
                else:
                    break

    def get_knight_move(self, r: int, c: int, moves: List[Move]):
        """Generate knight moves"""
        piece_pinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break

        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        ally_color = self.const.WHITE_PLAYER if self.white_to_move else self.const.BLACK_PLAYER
        
        for move in knight_moves:
            end_row = r + move[0]
            end_col = c + move[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                if not piece_pinned:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] != ally_color:
                        moves.append(Move((r, c), (end_row, end_col), self.board))

    def get_king_move(self, r: int, c: int, moves: List[Move]):
        """Generate king moves"""
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        ally_color = self.const.WHITE_PLAYER if self.white_to_move else self.const.BLACK_PLAYER
        
        for i in range(8):
            end_row = r + row_moves[i]
            end_col = c + col_moves[i]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:
                    # Check if move puts king in check
                    if ally_color == self.const.WHITE_PLAYER:
                        self.white_king_location = (end_row, end_col)
                    else:
                        self.black_king_location = (end_row, end_col)
                    
                    in_check, pins, checks = self.check_for_pins_and_checks()
                    if not in_check:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    
                    # Restore king position
                    if ally_color == self.const.WHITE_PLAYER:
                        self.white_king_location = (r, c)
                    else:
                        self.black_king_location = (r, c)

    def check_for_pins_and_checks(self) -> Tuple[bool, List[Tuple[int, int]], List[Tuple[int, int]]]:
        """Check for pins and checks"""
        pins = []
        checks = []
        in_check = False
        
        if self.white_to_move:
            enemy_color = self.const.BLACK_PLAYER
            ally_color = self.const.WHITE_PLAYER
            start_row, start_col = self.white_king_location
        else:
            enemy_color = self.const.WHITE_PLAYER
            ally_color = self.const.BLACK_PLAYER
            start_row, start_col = self.black_king_location
        
        directions = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        for j in range(len(directions)):
            direction = directions[j]
            possible_pin = ()
            for i in range(1, 8):
                end_row = start_row + direction[0] * i
                end_col = start_col + direction[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally_color and end_piece[1] != 'K':
                        if possible_pin == ():
                            possible_pin = (end_row, end_col, direction[0], direction[1])
                        else:
                            break
                    elif end_piece[0] == enemy_color:
                        piece_type = end_piece[1]
                        # Check if this piece can attack in this direction
                        if ((0 <= j <= 3 and piece_type == 'R') or 
                            (4 <= j <= 7 and piece_type == 'B') or 
                            (i == 1 and piece_type == 'p' and 
                             ((enemy_color == self.const.WHITE_PLAYER and 6 <= j <= 7) or 
                              (enemy_color == self.const.BLACK_PLAYER and 4 <= j <= 5))) or 
                            (piece_type == 'Q') or (i == 1 and piece_type == 'K')):
                            if possible_pin == ():
                                in_check = True
                                checks.append((end_row, end_col, direction[0], direction[1]))
                            else:
                                pins.append(possible_pin)
                        break
                else:
                    break
        
        # Check for knight checks
        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        for move in knight_moves:
            end_row = start_row + move[0]
            end_col = start_col + move[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece[1] == 'N':
                    in_check = True
                    checks.append((end_row, end_col, move[0], move[1]))
        
        return in_check, pins, checks

    def get_castle_moves(self, row: int, col: int, moves: List[Move]):
        """Generate castling moves"""
        if self.square_under_attack(row, col):
            return
        
        if ((self.white_to_move and self.current_castling_rights.wks) or 
            (not self.white_to_move and self.current_castling_rights.bks)):
            self.get_kingside_castle_moves(row, col, moves)
        
        if ((self.white_to_move and self.current_castling_rights.wqs) or 
            (not self.white_to_move and self.current_castling_rights.bqs)):
            self.get_queenside_castle_moves(row, col, moves)

    def get_kingside_castle_moves(self, row: int, col: int, moves: List[Move]):
        """Generate kingside castle moves"""
        if (self.board[row][col + 1] == self.const.EMPTY_POSITION and 
            self.board[row][col + 2] == self.const.EMPTY_POSITION):
            if (not self.square_under_attack(row, col + 1) and 
                not self.square_under_attack(row, col + 2)):
                moves.append(Move((row, col), (row, col + 2), self.board, is_castle_move=True))

    def get_queenside_castle_moves(self, row: int, col: int, moves: List[Move]):
        """Generate queenside castle moves"""
        if (self.board[row][col - 1] == self.const.EMPTY_POSITION and 
            self.board[row][col - 2] == self.const.EMPTY_POSITION and 
            self.board[row][col - 3] == self.const.EMPTY_POSITION):
            if (not self.square_under_attack(row, col - 1) and 
                not self.square_under_attack(row, col - 2)):
                moves.append(Move((row, col), (row, col - 2), self.board, is_castle_move=True))

    def square_under_attack(self, row: int, col: int) -> bool:
        """Check if square is under attack by opponent"""
        self.white_to_move = not self.white_to_move
        opponent_moves = self.get_all_possible_moves()
        self.white_to_move = not self.white_to_move
        
        for move in opponent_moves:
            if move.end_row == row and move.end_col == col:
                return True
        return False

    def is_valid_move(self, move: Move) -> bool:
        """Check if a move is valid in current position"""
        valid_moves = self.get_valid_moves()
        return move in valid_moves

    def copy(self):
        """Create a deep copy of the game state"""
        new_gs = GameState()
        new_gs.board = [row[:] for row in self.board]
        new_gs.white_to_move = self.white_to_move
        new_gs.move_log = self.move_log[:]
        new_gs.white_king_location = self.white_king_location
        new_gs.black_king_location = self.black_king_location
        new_gs.enPassant_possible = self.enPassant_possible
        new_gs.current_castling_rights = self.current_castling_rights.copy()
        new_gs.checkmate = self.checkmate
        new_gs.stalemate = self.stalemate
        new_gs.in_check = self.in_check
        new_gs.turn_num = self.turn_num
        return new_gs