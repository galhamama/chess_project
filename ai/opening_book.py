"""Chess opening book module for improved AI opening play"""

import json
import random
from typing import Dict, List, Optional, Tuple

class OpeningBook:
    """Chess opening book with popular openings and variations"""
    
    def __init__(self, book_file: str = None):
        """Initialize opening book with default openings or from file"""
        self.book = {}
        self.max_depth = 12  # Maximum opening moves to follow
        
        if book_file:
            self.load_from_file(book_file)
        else:
            self.initialize_default_book()
    
    def initialize_default_book(self):
        """Initialize with popular chess openings"""
        # Format: position_hash -> list of (move, weight, name)
        # Using algebraic notation for moves
        
        self.opening_lines = {
            # Starting position
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -": [
                ("e2e4", 45, "King's Pawn"),  # 1.e4
                ("d2d4", 40, "Queen's Pawn"),  # 1.d4
                ("g1f3", 10, "Reti Opening"),  # 1.Nf3
                ("c2c4", 5, "English Opening"),  # 1.c4
            ],
            
            # After 1.e4
            "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3": [
                ("e7e5", 30, "Open Game"),  # 1...e5
                ("c7c5", 25, "Sicilian Defense"),  # 1...c5
                ("e7e6", 15, "French Defense"),  # 1...e6
                ("c7c6", 15, "Caro-Kann Defense"),  # 1...c6
                ("d7d5", 10, "Scandinavian Defense"),  # 1...d5
                ("g8f6", 5, "Alekhine Defense"),  # 1...Nf6
            ],
            
            # After 1.e4 e5
            "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6": [
                ("g1f3", 60, "King's Knight"),  # 2.Nf3
                ("f2f4", 15, "King's Gambit"),  # 2.f4
                ("b1c3", 15, "Vienna Game"),  # 2.Nc3
                ("f1c4", 10, "Bishop's Opening"),  # 2.Bc4
            ],
            
            # After 1.e4 e5 2.Nf3
            "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq -": [
                ("b8c6", 70, "Normal"),  # 2...Nc6
                ("g8f6", 20, "Petroff Defense"),  # 2...Nf6
                ("f7f5", 10, "Latvian Gambit"),  # 2...f5
            ],
            
            # Italian Game: 1.e4 e5 2.Nf3 Nc6 3.Bc4
            "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq -": [
                ("f1c4", 40, "Italian Game"),  # 3.Bc4
                ("f1b5", 35, "Ruy Lopez"),  # 3.Bb5
                ("d2d4", 15, "Scotch Game"),  # 3.d4
                ("b1c3", 10, "Three Knights"),  # 3.Nc3
            ],
            
            # Sicilian Defense: 1.e4 c5
            "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6": [
                ("g1f3", 70, "Open Sicilian"),  # 2.Nf3
                ("b1c3", 20, "Closed Sicilian"),  # 2.Nc3
                ("c2c3", 10, "Alapin Variation"),  # 2.c3
            ],
            
            # After 1.e4 c5 2.Nf3
            "rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq -": [
                ("d7d6", 35, "Dragon/Najdorf setup"),  # 2...d6
                ("b8c6", 30, "Classical Sicilian"),  # 2...Nc6
                ("e7e6", 25, "Taimanov/Paulsen"),  # 2...e6
                ("g7g6", 10, "Hyperaccelerated Dragon"),  # 2...g6
            ],
            
            # French Defense: 1.e4 e6
            "rnbqkbnr/pppp1ppp/4p3/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -": [
                ("d2d4", 80, "Main Line"),  # 2.d4
                ("d2d3", 10, "King's Indian Attack"),  # 2.d3
                ("b1c3", 10, "Two Knights"),  # 2.Nc3
            ],
            
            # French Defense: 1.e4 e6 2.d4 d5
            "rnbqkbnr/ppp2ppp/4p3/3p4/3PP3/8/PPP2PPP/RNBQKBNR w KQkq d6": [
                ("b1c3", 35, "Classical French"),  # 3.Nc3
                ("b1d2", 30, "Tarrasch Variation"),  # 3.Nd2
                ("e4e5", 25, "Advance Variation"),  # 3.e5
                ("e4d5", 10, "Exchange Variation"),  # 3.exd5
            ],
            
            # Caro-Kann: 1.e4 c6
            "rnbqkbnr/pp1ppppp/2p5/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -": [
                ("d2d4", 70, "Main Line"),  # 2.d4
                ("b1c3", 20, "Two Knights"),  # 2.Nc3
                ("c2c4", 10, "Accelerated Panov"),  # 2.c4
            ],
            
            # After 1.d4
            "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq d3": [
                ("g8f6", 40, "Indian Defense"),  # 1...Nf6
                ("d7d5", 35, "Queen's Gambit"),  # 1...d5
                ("f7f5", 10, "Dutch Defense"),  # 1...f5
                ("e7e6", 10, "French-like"),  # 1...e6
                ("g7g6", 5, "Modern Defense"),  # 1...g6
            ],
            
            # Queen's Gambit: 1.d4 d5
            "rnbqkbnr/ppp1pppp/8/3p4/3P4/8/PPP1PPPP/RNBQKBNR w KQkq d6": [
                ("c2c4", 90, "Queen's Gambit"),  # 2.c4
                ("g1f3", 10, "London System setup"),  # 2.Nf3
            ],
            
            # Queen's Gambit: 1.d4 d5 2.c4
            "rnbqkbnr/ppp1pppp/8/3p4/2PP4/8/PP2PPPP/RNBQKBNR b KQkq c3": [
                ("e7e6", 40, "Queen's Gambit Declined"),  # 2...e6
                ("d5c4", 30, "Queen's Gambit Accepted"),  # 2...dxc4
                ("c7c6", 20, "Slav Defense"),  # 2...c6
                ("e7e5", 10, "Albin Counter-Gambit"),  # 2...e5
            ],
            
            # Indian Defense: 1.d4 Nf6
            "rnbqkb1r/pppppppp/5n2/8/3P4/8/PPP1PPPP/RNBQKBNR w KQkq -": [
                ("c2c4", 60, "Indian Systems"),  # 2.c4
                ("g1f3", 25, "London/Torre"),  # 2.Nf3
                ("b1c3", 15, "Veresov"),  # 2.Nc3
            ],
            
            # After 1.d4 Nf6 2.c4
            "rnbqkb1r/pppppppp/5n2/8/2PP4/8/PP2PPPP/RNBQKBNR b KQkq c3": [
                ("e7e6", 30, "Nimzo/Queen's Indian"),  # 2...e6
                ("g7g6", 30, "King's Indian Defense"),  # 2...g6
                ("e7e5", 20, "Budapest Gambit"),  # 2...e5
                ("c7c5", 20, "Benoni"),  # 2...c5
            ],
            
            # King's Indian: 1.d4 Nf6 2.c4 g6
            "rnbqkb1r/pppppp1p/5np1/8/2PP4/8/PP2PPPP/RNBQKBNR w KQkq -": [
                ("b1c3", 60, "Classical KID"),  # 3.Nc3
                ("g1f3", 30, "King's Indian"),  # 3.Nf3
                ("f2f3", 10, "Samisch Variation"),  # 3.f3
            ],
            
            # Nimzo-Indian: 1.d4 Nf6 2.c4 e6
            "rnbqkb1r/pppp1ppp/4pn2/8/2PP4/8/PP2PPPP/RNBQKBNR w KQkq -": [
                ("b1c3", 70, "Nimzo-Indian"),  # 3.Nc3
                ("g1f3", 20, "Queen's Indian"),  # 3.Nf3
                ("g2g3", 10, "Catalan"),  # 3.g3
            ],
            
            # Ruy Lopez: 1.e4 e5 2.Nf3 Nc6 3.Bb5
            "r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq -": [
                ("a7a6", 60, "Morphy Defense"),  # 3...a6
                ("g8f6", 20, "Berlin Defense"),  # 3...Nf6
                ("f7f5", 10, "Schliemann Defense"),  # 3...f5
                ("f8c5", 10, "Classical Defense"),  # 3...Bc5
            ],
            
            # Ruy Lopez Morphy: 1.e4 e5 2.Nf3 Nc6 3.Bb5 a6
            "r1bqkbnr/1ppp1ppp/p1n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R w KQkq -": [
                ("b5a4", 70, "Main Line"),  # 4.Ba4
                ("b5c6", 20, "Exchange Variation"),  # 4.Bxc6
                ("b5c4", 10, "Neo-Arkhangelsk"),  # 4.Bc4
            ],
            
            # English Opening: 1.c4
            "rnbqkbnr/pppppppp/8/8/2P5/8/PP1PPPPP/RNBQKBNR b KQkq c3": [
                ("e7e5", 35, "Reversed Sicilian"),  # 1...e5
                ("g8f6", 30, "Indian setup"),  # 1...Nf6
                ("c7c5", 20, "Symmetrical"),  # 1...c5
                ("e7e6", 15, "Agincourt Defense"),  # 1...e6
            ],
            
            # Reti Opening: 1.Nf3
            "rnbqkbnr/pppppppp/8/8/8/5N2/PPPPPPPP/RNBQKB1R b KQkq -": [
                ("d7d5", 40, "Classical"),  # 1...d5
                ("g8f6", 30, "Indian setup"),  # 1...Nf6
                ("c7c5", 20, "Sicilian-like"),  # 1...c5
                ("f7f5", 10, "Dutch setup"),  # 1...f5
            ],
        }
        
        # Convert to internal format
        self._build_book_from_lines()
    
    def _build_book_from_lines(self):
        """Convert opening lines to internal book format"""
        self.book = {}
        for fen, moves in self.opening_lines.items():
            self.book[fen] = moves
    
    def get_fen_from_board(self, board, white_to_move: bool, 
                        castle_rights, en_passant) -> str:
        """Convert board position to FEN string for lookup"""
        fen_rows = []
        
        for row in board:
            fen_row = ""
            empty_count = 0
            
            for square in row:
                if square == "--":
                    empty_count += 1
                else:
                    if empty_count > 0:
                        fen_row += str(empty_count)
                        empty_count = 0
                    
                    # Convert piece notation correctly
                    color = square[0]  # 'w' or 'b'
                    piece = square[1]  # 'p', 'R', 'N', 'B', 'Q', 'K'
                    
                    # In FEN: uppercase = white, lowercase = black
                    if color == 'w':
                        fen_row += piece.upper()  # Uppercase ALL white pieces
                    else:
                        fen_row += piece.lower()  # Lowercase ALL black pieces
            
            if empty_count > 0:
                fen_row += str(empty_count)
            
            fen_rows.append(fen_row)
        
        # Rest of the method stays the same...
        fen = "/".join(fen_rows)
        
        # Add side to move
        fen += " w" if white_to_move else " b"
        
        # Add castling rights
        castle_str = ""
        if castle_rights:
            if castle_rights.wks: castle_str += "K"
            if castle_rights.wqs: castle_str += "Q"
            if castle_rights.bks: castle_str += "k"
            if castle_rights.bqs: castle_str += "q"
        if not castle_str:
            castle_str = "-"
        fen += " " + castle_str
        
        # Add en passant
        if en_passant and len(en_passant) == 2:
            ep_col = "abcdefgh"[en_passant[1]]
            ep_row = str(8 - en_passant[0])
            fen += " " + ep_col + ep_row
        else:
            fen += " -"
        
        return fen
        
    def get_book_move(self, board, white_to_move: bool,
                    castle_rights, en_passant, 
                    move_history) -> Optional[Tuple[Tuple[int, int], Tuple[int, int], str]]:
        """Get a move from the opening book"""
        # Check if we're still in opening phase
        if move_history and len(move_history) > self.max_depth:
            return None
        
        # Get FEN position
        fen = self.get_fen_from_board(board, white_to_move, castle_rights, en_passant)
        
        print(f"DEBUG: Current FEN: {fen}")
        print(f"DEBUG: Move history length: {len(move_history) if move_history else 0}")

        # Look up position in book
        if fen in self.book:
            moves = self.book[fen]
            print(f"DEBUG: Found {len(moves)} book moves!")
            
            # Select move based on weights
            total_weight = sum(weight for _, weight, _ in moves)
            if total_weight == 0:
                return None
            
            # Random weighted selection
            rand_val = random.random() * total_weight
            cumulative = 0
            
            for move_str, weight, name in moves:
                cumulative += weight
                if rand_val <= cumulative:
                    # Convert algebraic to board coordinates
                    coords = self.algebraic_to_move(move_str)
                    if coords:
                        return coords[0], coords[1], name
            
            # Fallback to first move
            coords = self.algebraic_to_move(moves[0][0])
            if coords:
                return coords[0], coords[1], moves[0][2]
        
        print(f"DEBUG: Position not in book")
        return None
    
    def algebraic_to_move(self, move_str: str) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Convert algebraic notation (e2e4) to board coordinates"""
        if len(move_str) != 4:
            return None
        
        from_col = ord(move_str[0]) - ord('a')
        from_row = 8 - int(move_str[1])
        to_col = ord(move_str[2]) - ord('a')
        to_row = 8 - int(move_str[3])
        
        return ((from_row, from_col), (to_row, to_col))
    
    def save_to_file(self, filename: str):
        """Save opening book to JSON file"""
        with open(filename, 'w') as f:
            json.dump({
                'book': self.book,
                'max_depth': self.max_depth
            }, f, indent=2)
    
    def load_from_file(self, filename: str):
        """Load opening book from JSON file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                self.book = data.get('book', {})
                self.max_depth = data.get('max_depth', 12)
                print(f"Loaded opening book with {len(self.book)} positions")
        except FileNotFoundError:
            print(f"Opening book file {filename} not found. Using default openings.")
            self.initialize_default_book()
        except json.JSONDecodeError:
            print(f"Error reading opening book file {filename}. Using default openings.")
            self.initialize_default_book()