"""Main game view and rendering"""

from __future__ import annotations
import pygame as p
import math
from typing import TYPE_CHECKING

from controllers.game_controller import GameController
from .menu_system import MainMenu
from .ui_components import Button

if TYPE_CHECKING:
    from core.move import Move

class GameView:
    def __init__(self):
        """Main game view responsible for rendering the chess game"""
        
        self.controller = GameController()
        self.constants = self.controller.constants
        self.width = self.height = self.constants.HEIGHT
        self.dimension = self.constants.DIMENSION 
        self.sq_size = self.constants.SQ_SIZE 
        self.max_fps = self.constants.MAX_FPS
        self.images = self.constants.IMAGE 
        self.colors: list[tuple[int,int,int]] = [self.constants.LIGHT_GRAY, self.constants.DARK_BLUE] 
        
        # Pygame setup
        self.clock = p.time.Clock()
        self.screen = p.display.set_mode((self.width + self.constants.SIDE_SCREEN, self.height))
        p.display.set_caption("Advanced Chess Engine")
        
        # UI state
        self.promote = self.controller.promote
        self.save_button = Button(self.constants.DARK_GRAY, 550, 400, 100, 50, "save")
        self.load_button = Button(self.constants.DARK_GRAY, 550, 460, 100, 50, "load")

    def load_images(self):
        """Load piece images based on board pieces"""
        pieces = ["wp","wR","wN","wB","wQ","wK","bp","bR","bN","bB","bQ","bK"]
        for piece in pieces:
            try:
                image_path = f"assets/images/pieces/{piece}.png"
                self.images[piece] = p.transform.scale(
                    p.image.load(image_path), 
                    (self.sq_size, self.sq_size)
                )
            except Exception as e:
                print(f"Error loading image {piece}: {e}")
                # Create a placeholder colored rectangle
                placeholder = p.Surface((self.sq_size, self.sq_size))
                color = (255, 255, 255) if piece[0] == 'w' else (0, 0, 0)
                placeholder.fill(color)
                self.images[piece] = placeholder

    def main(self):
        """Main game loop"""
        p.init()
        screen = self.screen
        clock = self.clock
        screen.fill(self.constants.DIM_BLUE)
        self.load_images()
        running = True
        
        while running:
            # Handle events
            for event in p.event.get():
                if event.type == p.QUIT:
                    running = False
                    self.controller.terminate()
                    p.quit()

                elif event.type == p.MOUSEBUTTONDOWN:
                    location = p.mouse.get_pos()
                    if location[0] < self.constants.WIDTH:
                        self.controller.handle_mouse_click(location)
                    self.check_save_buttons(location)
                    
                elif event.type == p.KEYDOWN:
                    if event.key == p.K_z:  # Undo move
                        self.controller.undo_move()
                    elif event.key == p.K_r:  # Reset board
                        self.controller.reset_game()
                    elif event.key == p.K_ESCAPE:  # Return to menu
                        self.controller.reset_game()
                        menu = MainMenu(self)
                        menu.draw_main_menu()
                        
                # Handle pawn promotion
                if self.controller.needs_pawn_promotion() and self.promote:
                    self.draw_pawn_promotion()
                    
            # Update game state
            self.draw_game_state(screen, self.controller.get_valid_moves(), 
                               self.controller.get_selected_square())
            clock.tick(self.max_fps)
            
            # Handle AI moves
            self.controller.handle_random_move()
            self.controller.handle_ai_move()
            self.controller.process_moves(screen, clock, self)

            p.display.flip()

    def draw_game_state(self, screen: p.surface, valid_moves: list[Move], sq_selected: tuple[int,int]):
        """Draw the current state of the game"""
        self.draw_board(screen)
        self.highlight_squares(screen, valid_moves, sq_selected)
        self.draw_pieces(screen, self.controller.get_board())
        self.draw_side_panel(screen)

    def highlight_squares(self, screen: p.surface, valid_moves: list[Move], sq_selected: tuple[int,int]):
        """Highlight selected square and valid moves"""
        if sq_selected != ():
            r, c = sq_selected
            if self.controller.get_board()[r][c][0] == ('w' if self.controller.is_white_turn() else 'b'): 
                # Highlight selected square
                surface = p.Surface((self.sq_size, self.sq_size))
                surface.set_alpha(100)
                surface.fill((0, 0, 128))
                screen.blit(surface, (c * self.sq_size, r * self.sq_size))
                
                # Highlight valid moves
                surface.fill((135, 206, 250))
                for move in valid_moves:
                    if move.start_row == r and move.start_col == c:
                        screen.blit(surface, (move.end_col * self.sq_size, move.end_row * self.sq_size))
                
                # Highlight last move
                move_log = self.controller.get_move_log()
                if len(move_log) != 0:
                    last_move = move_log[-1]
                    surface.fill((0, 255, 0))
                    screen.blit(surface, (last_move.end_col * self.sq_size, last_move.end_row * self.sq_size))

    def draw_board(self, screen: p.surface):
        """Draw the chess board squares"""
        for r in range(self.dimension):
            for c in range(self.dimension):
                color = self.colors[((r + c) % 2)]
                p.draw.rect(screen, color, p.Rect(c * self.sq_size, r * self.sq_size, self.sq_size, self.sq_size))

    def draw_pieces(self, screen: p.surface, board: list[list[str]]):
        """Draw pieces on the board"""
        for r in range(self.dimension):
            for c in range(self.dimension):
                piece = board[r][c]
                if piece != self.constants.EMPTY_POSITION:
                    screen.blit(self.images[piece], p.Rect(c * self.sq_size, r * self.sq_size, self.sq_size, self.sq_size))
    
    def draw_side_panel(self, screen: p.surface):
        """Draw the side information panel"""
        p.draw.rect(screen, self.constants.DIM_BLUE, (512, 0, 200, 512))
        self.draw_turn_indicator(screen)
        self.draw_move_log(screen)
        if self.controller.ai_is_thinking:
            self.draw_ai_stats(screen)
        self.draw_save_buttons(self.save_button, self.load_button, screen)

    def draw_turn_indicator(self, screen):
        """Draw whose turn it is"""
        color = self.constants.WHITE if self.controller.is_white_turn() else self.constants.BLACK
        p.draw.rect(screen, color, p.Rect(537, 50, 150, 100))
        
        # Add text
        font = p.font.SysFont('Arial', 24)
        turn_text = "White" if self.controller.is_white_turn() else "Black"
        text_color = self.constants.BLACK if self.controller.is_white_turn() else self.constants.WHITE
        text_surface = font.render(f"{turn_text}'s Turn", True, text_color)
        screen.blit(text_surface, (545, 90))
        
    def draw_move_log(self, screen):
        """Draw the move history"""
        move_log = self.controller.get_move_log()
        font = p.font.SysFont(None, 24)
        title = font.render("Move Log", True, self.constants.WHITE)
        screen.blit(title, (612 - 40, 180))
        
        # Display last 16 moves
        limit = 12
        if len(move_log) > limit:
            move_log = move_log[-limit:]
            
        for i, move in enumerate(move_log):
            text = move.get_chess_notation() + ","
            img = font.render(text, True, self.constants.WHITE)
            screen.blit(img, (520 + 45 * (i % 4), 200 + 25 * math.ceil((i + 1) / 4)))

    def draw_ai_stats(self, screen):
        """Draw AI performance statistics"""
        stats = self.controller.get_ai_stats()
        font = p.font.SysFont(None, 20)
        y_offset = 300
        
        stat_lines = [
            f"AI Moves: {stats.get('moves_made', 0)}",
            f"Avg Time: {stats.get('average_time', 0):.1f}s",
            f"Depth: {stats.get('current_depth', 0)}",
            f"Nodes: {stats.get('nodes_searched', 0):,}"
        ]
        
        for i, line in enumerate(stat_lines):
            text_surface = font.render(line, True, self.constants.WHITE)
            screen.blit(text_surface, (520, y_offset + i * 20))

    def draw_save_buttons(self, save_button: Button, load_button: Button, screen):
        """Draw save and load buttons"""
        save_button.draw(screen)
        load_button.draw(screen)
    
    def check_save_buttons(self, location):
        """Handle save/load button clicks"""
        if self.save_button.is_over(location):
            self.controller.save_game()
        elif self.load_button.is_over(location):
            self.controller.load_game()

    def animate_move(self, move: Move, screen: p.surface, board: list[list[str]], clock: p.time.Clock):
        """Animate a move being played"""
        colors = self.colors
        dR = move.end_row - move.start_row
        dC = move.end_col - move.start_col
        frame_per_square = 6  # Frames per square moved
        frame_count = (abs(dR) + abs(dC)) * frame_per_square
        
        for frame in range(frame_count + 1):
            r = move.start_row + dR * frame / frame_count
            c = move.start_col + dC * frame / frame_count
            
            self.draw_board(screen)
            self.draw_pieces(screen, board)
            
            # Clear the destination square
            color = colors[(move.end_row + move.end_col) % 2]
            end_square = p.Rect(move.end_col * self.sq_size, move.end_row * self.sq_size, self.sq_size, self.sq_size)
            p.draw.rect(screen, color, end_square)
            
            # Draw captured piece (if any)
            if move.piece_captured != self.constants.EMPTY_POSITION:
                if move.enPassant:
                    enPassantRow = move.end_row + 1 if move.piece_captured[0] == 'b' else move.end_row - 1
                    end_square = p.Rect(move.end_col * self.sq_size, enPassantRow * self.sq_size, self.sq_size, self.sq_size)
                screen.blit(self.images[move.piece_captured], end_square)
            
            # Draw moving piece
            screen.blit(self.images[move.piece_moved], p.Rect(c * self.sq_size, r * self.sq_size, self.sq_size, self.sq_size))
            p.display.flip()
            clock.tick(60)
        
    def draw_text(self, screen: p.surface, text: str):
        """Draw centered text (for game over messages)"""
        font = p.font.SysFont("Helvetica", 32, True, False)
        text_object = font.render(text, True, p.Color('Black'))
        text_location = p.Rect(0, 0, self.width, self.height).move(
            self.width/2 - text_object.get_width()/2, 
            self.height/2 - text_object.get_height()/2
        )
        screen.blit(text_object, text_location)

    def draw_promotion_buttons(self, q: Button, r: Button, b: Button, n: Button):
        """Draw pawn promotion choice buttons"""
        q.draw(self.screen)
        r.draw(self.screen)
        b.draw(self.screen)
        n.draw(self.screen)

    def draw_pawn_promotion(self):
        """Handle pawn promotion UI"""
        q = Button((105, 105, 105), self.width/2 - 30, self.height/2, 60, 60, "Q")
        r = Button((105, 105, 105), self.width/2 + 30, self.height/2, 60, 60, "R")
        b = Button((105, 105, 105), self.width/2 - 30, self.height/2 - 70, 60, 60, "B")
        n = Button((105, 105, 105), self.width/2 + 30, self.height/2 - 70, 60, 60, "N")
        
        running = True
        while running:
            for event in p.event.get():
                if event.type == p.QUIT:
                    running = False
                    
                elif event.type == p.MOUSEBUTTONDOWN:
                    location = p.mouse.get_pos()
                    if q.is_over(location):
                        self.controller.set_promotion_piece("Q")
                        running = False
                        self.promote = False
                    elif r.is_over(location):
                        self.controller.set_promotion_piece("R")
                        running = False
                        self.promote = False