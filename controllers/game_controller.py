"""Game controller handling user input and game flow"""

from __future__ import annotations
import threading
import queue
from typing import List, Dict, Any, Tuple

from core import GameState, Move, ConstantValues, SaveManager
from ai import AdvancedChessAI

class GameController:
    def __init__(self):
        """Initialize game controller with enhanced AI integration"""
        
        # Core game components
        self.constants = ConstantValues()
        self.game_state = GameState()
        self.ai = AdvancedChessAI(self.game_state)
        self.save_manager = SaveManager()
        
        # Game state
        self.valid_moves = self.game_state.get_valid_moves()
        self.sq_size = self.constants.SQ_SIZE
        self.move_made = self.game_state.move_made
        self.animate_move = self.game_state.animate_move
        self.game_over = self.game_state.game_over
        self.sq_selected = self.game_state.sq_selected 
        self.player_clicks = self.game_state.player_clicks
        
        # AI threading
        self.return_queue = queue.Queue()
        self.ai_is_thinking = False
        self.move_find_thread = None
        self.undo_move_flag = False
        
        # Game mode settings
        self.player_one = True   # White player is human
        self.player_two = True   # Black player is human
        self.random_turn = False # Random move mode
        self.promote = True      # Pawn promotion UI flag
        
        # AI performance settings
        self.ai_time_limit = 5.0
        self.ai_depth = 6
        
        # Statistics
        self.total_ai_time = 0.0
        self.ai_moves_made = 0

    # Game mode setters
    def set_player_vs_player(self):
        """Set game mode to human vs human"""
        self.player_one = True
        self.player_two = True
        self.random_turn = False

    def set_ai_vs_ai(self):
        """Set game mode to AI vs AI"""
        self.player_one = False
        self.player_two = False
        self.random_turn = False

    def set_ai_black(self):
        """Set game mode to human vs AI (AI plays black)"""
        self.player_one = True
        self.player_two = False
        self.random_turn = False

    def set_ai_white(self):
        """Set game mode to AI vs human (AI plays white)"""
        self.player_one = False
        self.player_two = True
        self.random_turn = False
        
    def set_random_vs_ai(self):
        """Set game mode to random vs AI"""
        self.player_one = False
        self.player_two = True
        self.random_turn = True

    # Getters for UI
    def needs_pawn_promotion(self) -> bool:
        """Check if pawn promotion is needed"""
        if len(self.game_state.move_log) != 0:
            return self.game_state.move_log[-1].pawn_promotion
        return False
    
    def set_promotion_piece(self, piece: str):
        """Set piece for pawn promotion"""
        if self.is_human_turn():
            self.game_state.player_promote = True
            self.game_state.promotion_piece = piece

    def get_valid_moves(self) -> List[Move]:
        return self.valid_moves

    def get_selected_square(self) -> Tuple[int, int]:
        return self.sq_selected

    def get_board(self) -> List[List[str]]:
        return self.game_state.board

    def is_white_turn(self) -> bool:
        return self.game_state.white_to_move

    def is_human_turn(self) -> bool:
        return ((self.game_state.white_to_move and self.player_one) or 
                (not self.game_state.white_to_move and self.player_two))

    def get_move_log(self) -> List[Move]:
        return self.game_state.move_log

    # Input handling
    def handle_mouse_click(self, location: Tuple[int, int]):
        """Handle mouse clicks on the board"""
        if not self.game_over and not self.random_turn:
            col = location[0] // self.sq_size
            row = location[1] // self.sq_size
            
            if self.sq_selected == (row, col):
                # Deselect if clicking same square
                self.sq_selected = ()
                self.player_clicks = []
            else:
                self.sq_selected = (row, col)
                self.player_clicks.append(self.sq_selected)
                
                # Process move if two squares selected
                if len(self.player_clicks) == 2 and self.is_human_turn():
                    attempted_move = Move(
                        self.player_clicks[0], 
                        self.player_clicks[1], 
                        self.game_state.board
                    )
                    print(f"Player attempting: {attempted_move.get_chess_notation()}")
                    
                    # Find matching valid move
                    for valid_move in self.valid_moves:
                        if attempted_move == valid_move:
                            self.promote = True
                            self.game_state.make_move(valid_move)
                            self.move_made = True
                            valid_move.set_last_moved(self.game_state.turn_num)
                            self.animate_move = True
                            self.promote = False
                            self.sq_selected = ()
                            self.player_clicks = []
                            print(f"Move executed: {valid_move.get_chess_notation()}")
                            break
                    
                    if not self.move_made:
                        # Invalid move, keep first click
                        self.player_clicks = [self.sq_selected]

    def handle_random_move(self):
        """Handle random moves when in random mode"""
        if self.random_turn and self.is_human_turn() and not self.game_over:
            if self.valid_moves:
                random_move = self.ai.find_random_move(self.valid_moves)
                if random_move:
                    print(f"Random move: {random_move.get_chess_notation()}")
                    self.game_state.make_move(random_move)
                    random_move.set_last_moved(self.game_state.turn_num)
                    self.move_made = True
                    self.animate_move = True
                    self.ai_is_thinking = False
                    self.promote = False

    def undo_move(self):
        """Undo the last move"""
        if self.game_state.turn_num > 0 and len(self.game_state.move_log) > 0:
            print("Undoing move...")
            self.game_state.turn_num -= 1
            self.game_state.move_log[-1].set_last_moved(self.game_state.turn_num)
            self.game_state.undo_move()
            self.move_made = True
            self.animate_move = False
            self.game_over = False
            
            # Cancel AI search if in progress
            if self.ai_is_thinking:
                self.ai.cancel_search_now()
                if self.move_find_thread and self.move_find_thread.is_alive():
                    self.move_find_thread.join(timeout=0.5)
                self.ai_is_thinking = False
                print("AI search cancelled")
            
            self.undo_move_flag = True

    def handle_ai_move(self):
        """Handle AI move generation and execution"""
        if not self.game_over and not self.undo_move_flag and not self.is_human_turn():
            if not self.ai_is_thinking:
                # Start AI thinking
                self.ai_is_thinking = True
                
                # Update valid moves
                self.valid_moves = self.game_state.get_valid_moves()
                
                if not self.valid_moves:
                    print("No valid moves available for AI")
                    self.ai_is_thinking = False
                    return
                
                # Clear previous results
                while not self.return_queue.empty():
                    try:
                        self.return_queue.get_nowait()
                    except queue.Empty:
                        break
                
                # Configure AI for current position
                self.configure_ai_for_position()
                
                print(f"AI thinking (depth={self.ai.max_depth}, time={self.ai.time_limit}s)...")
                
                # Start AI search thread
                self.move_find_thread = threading.Thread(
                    target=self.ai.find_best_move,
                    args=(self.game_state, list(self.valid_moves), self.return_queue),
                    daemon=True
                )
                self.move_find_thread.start()
                
            # Check if AI search is complete
            elif not self.move_find_thread.is_alive():
                try:
                    ai_move = self.return_queue.get_nowait()
                    
                    if ai_move is None:
                        print("AI returned no move, using random fallback")
                        ai_move = self.ai.find_random_move(self.valid_moves)
                    
                    if ai_move:
                        print(f"AI selected: {ai_move.get_chess_notation()}")
                        self.promote = True
                        self.game_state.make_move(ai_move)
                        ai_move.set_last_moved(self.game_state.turn_num)
                        self.move_made = True
                        self.animate_move = True
                        self.ai_is_thinking = False
                        self.promote = False
                        
                        # Update statistics
                        self.ai_moves_made += 1
                        print(f"AI move #{self.ai_moves_made} completed")
                    else:
                        print("No AI move available")
                        self.ai_is_thinking = False
                        
                except queue.Empty:
                    # AI still thinking - this is normal
                    pass

    def configure_ai_for_position(self):
        """Configure AI parameters based on game stage"""
        # Count pieces to determine game stage
        piece_count = sum(1 for row in self.game_state.board 
                         for square in row if square != "--")
        
        # Adjust AI parameters based on game stage
        if piece_count > 24:  # Opening
            self.ai.time_limit = min(self.ai_time_limit, 3.0)
            self.ai.max_depth = min(self.ai_depth, 5)
        elif piece_count > 12:  # Middlegame
            self.ai.time_limit = self.ai_time_limit
            self.ai.max_depth = self.ai_depth
        else:  # Endgame
            self.ai.time_limit = min(self.ai_time_limit * 1.5, 8.0)
            self.ai.max_depth = min(self.ai_depth + 1, 10)

    def process_moves(self, screen, clock, view):
        """Process move execution and game state updates"""
        if self.move_made:
            self.game_state.turn_num += 1
            
            if self.animate_move:
                view.animate_move(self.game_state.move_log[-1], screen, 
                                self.game_state.board, clock)
            
            # Update valid moves and check for game end
            self.valid_moves = self.game_state.get_valid_moves()
            self.move_made = False
            self.animate_move = False
            self.undo_move_flag = False
            
            # Check for checkmate/stalemate
            if len(self.valid_moves) == 0:
                if self.game_state.in_check:
                    self.game_state.checkmate = True
                else:
                    self.game_state.stalemate = True
        
        # Display game end messages
        if self.game_state.checkmate:
            self.game_over = True
            winner = "Black" if self.game_state.white_to_move else "White"
            view.draw_text(screen, f"{winner} wins by checkmate")
        elif self.game_state.stalemate:
            self.game_over = True
            view.draw_text(screen, "Draw by stalemate")

    # Game management
    def reset_game(self):
        """Reset the game to initial state"""
        print("Resetting game...")
        
        # Cancel any ongoing AI search
        if self.ai_is_thinking:
            self.ai.cancel_search_now()
            if self.move_find_thread and self.move_find_thread.is_alive():
                self.move_find_thread.join(timeout=1.0)
            self.ai_is_thinking = False
        
        # Reset game state
        self.game_state = GameState()
        self.ai.gs = self.game_state  # Update AI reference
        self.ai.tt.clear()   # Clear transposition table
        
        # Reset controller state
        self.move_made = True
        self.animate_move = False
        self.game_over = False
        self.undo_move_flag = True
        self.sq_selected = ()
        self.player_clicks = []
        
        # Reset statistics
        self.total_ai_time = 0.0
        self.ai_moves_made = 0
        
        print("Game reset complete")

    def save_game(self):
        """Save current game state"""
        ai_settings = {
            'ai_depth': self.ai_depth,
            'ai_time_limit': self.ai_time_limit,
            'player_one': self.player_one,
            'player_two': self.player_two
        }
        
        success = self.save_manager.save_game(self.game_state, ai_settings)
        if success:
            print("Game saved successfully")
        else:
            print("Failed to save game")

    def load_game(self):
        """Load saved game state"""
        save_data = self.save_manager.load_game()
        if save_data:
            self.game_state = save_data['game_state']
            
            # Load AI settings if available
            ai_settings = save_data.get('ai_settings', {})
            self.ai_depth = ai_settings.get('ai_depth', 6)
            self.ai_time_limit = ai_settings.get('ai_time_limit', 5.0)
            self.player_one = ai_settings.get('player_one', True)
            self.player_two = ai_settings.get('player_two', True)
            
            # Update AI reference and clear cache
            self.ai.gs = self.game_state
            self.ai.tt.clear()
            
            # Update valid moves
            self.valid_moves = self.game_state.get_valid_moves()
            self.move_made = True
            
            print("Game loaded successfully")
        else:
            print("Failed to load game")

    def set_ai_difficulty(self, level: int):
        """Set AI difficulty level (1=Easy, 2=Normal, 3=Hard)"""
        if level == 1:  # Easy
            self.ai_depth = 4
            self.ai_time_limit = 2.0
            print("AI difficulty: Easy (depth=4, time=2s)")
        elif level == 2:  # Normal
            self.ai_depth = 6
            self.ai_time_limit = 5.0
            print("AI difficulty: Normal (depth=6, time=5s)")
        elif level == 3:  # Hard
            self.ai_depth = 8
            self.ai_time_limit = 10.0
            print("AI difficulty: Hard (depth=8, time=10s)")
        else:
            self.ai_depth = 6
            self.ai_time_limit = 5.0
        
        # Update AI settings
        self.ai.set_difficulty(level)
    
    def get_ai_stats(self) -> Dict[str, Any]:
        """Get AI performance statistics"""
        return {
            'moves_made': self.ai_moves_made,
            'average_time': self.total_ai_time / max(self.ai_moves_made, 1),
            'current_depth': self.ai_depth,
            'time_limit': self.ai_time_limit,
            'tt_hit_rate': self.ai.tt.get_hit_rate(),
            'nodes_searched': getattr(self.ai, 'nodes_searched', 0)
        }

    def get_position_analysis(self) -> Dict[str, Any]:
        """Get analysis of current position"""
        # Quick position evaluation
        board_copy = [row[:] for row in self.game_state.board]
        evaluation = self.ai.evaluate_position(board_copy, self.game_state.white_to_move)
        
        # Count material and pieces
        material_balance = 0
        piece_count = 0
        for row in self.game_state.board:
            for square in row:
                if square != "--":
                    piece_count += 1
                    value = self.ai.piece_values.get(square[1], 0)
                    if square[0] == 'w':
                        material_balance += value
                    else:
                        material_balance -= value
        
        return {
            'evaluation': evaluation,
            'material_balance': material_balance,
            'piece_count': piece_count,
            'game_stage': 'opening' if piece_count > 24 else 'middlegame' if piece_count > 12 else 'endgame',
            'valid_moves': len(self.valid_moves)
        }

    def terminate(self):
        """Clean up resources when exiting"""
        print("Terminating controller...")
        
        if self.ai_is_thinking:
            print("Cancelling AI search...")
            self.ai.cancel_search_now()
        
        if self.move_find_thread and self.move_find_thread.is_alive():
            self.move_find_thread.join(timeout=2.0)
            if self.move_find_thread.is_alive():
                print("Warning: AI thread did not terminate cleanly")
        
        # Print final statistics
        if self.ai_moves_made > 0:
            avg_time = self.total_ai_time / self.ai_moves_made
            print(f"AI Statistics: {self.ai_moves_made} moves, {avg_time:.2f}s average")