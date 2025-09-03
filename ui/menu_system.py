"""Menu system for chess game navigation"""

import pygame as p
from .ui_components import Button

class MainMenu:
    def __init__(self, game_view):
        """Main menu system for the chess game"""
        self.view = game_view
        self.controller = game_view.controller
        self.constants = self.view.constants
        self.screen = game_view.screen
        self.screen_width = self.view.width
        self.screen_height = self.view.height 
        
        # Button styling
        self.button_color = self.constants.DARK_GRAY
        button_width = self.screen_width // 2
        button_height = self.screen_height // 8
        
        # Main menu buttons
        self.button_play = Button(
            self.button_color, 
            self.screen_width//4 + self.constants.MENU_OFFSET,
            self.screen_height//2 + 60, 
            button_width, button_height, "Play"
        )
        self.button_rules = Button(
            self.button_color,
            self.screen_width//4 + self.constants.MENU_OFFSET,
            self.screen_height//2 + 140,
            button_width, button_height, "Rules"
        )
        self.button_controls = Button(
            self.button_color,
            self.screen_width//4 + self.constants.MENU_OFFSET,
            self.screen_height//2 - 20,
            button_width, button_height, "Controls"
        )
        
        # Play menu buttons
        self.button_pvp = Button(
            self.button_color,
            self.screen_width//4 + self.constants.MENU_OFFSET,
            self.screen_height//2 + 60,
            button_width, button_height, "Player vs Player"
        )
        self.button_pva = Button(
            self.button_color,
            self.screen_width//4 + self.constants.MENU_OFFSET,
            self.screen_height//2 - 20,
            button_width, button_height, "Player vs AI"
        )
        self.button_ai_menu = Button(
            self.button_color,
            self.screen_width//4 + self.constants.MENU_OFFSET,
            self.screen_height//2 + 140,
            button_width, button_height, "AI Options"
        )
        
        # AI selection buttons
        self.button_ai_black = Button(
            self.button_color,
            self.screen_width//4 + self.constants.MENU_OFFSET,
            self.screen_height//2 + 60,
            button_width, button_height, "AI Black"
        )
        self.button_ai_white = Button(
            self.button_color,
            self.screen_width//4 + self.constants.MENU_OFFSET,
            self.screen_height//2 - 20,
            button_width, button_height, "AI White"
        )
        
        # Difficulty buttons
        self.button_easy = Button(
            self.button_color,
            self.screen_width//4 + self.constants.MENU_OFFSET,
            self.screen_height//2 - 20,
            button_width, button_height, "Easy"
        )
        self.button_normal = Button(
            self.button_color,
            self.screen_width//4 + self.constants.MENU_OFFSET,
            self.screen_height//2 + 60,
            button_width, button_height, "Normal"
        )
        self.button_hard = Button(
            self.button_color,
            self.screen_width//4 + self.constants.MENU_OFFSET,
            self.screen_height//2 + 140,
            button_width, button_height, "Hard"
        )
        
        # AI vs AI buttons
        self.button_ai_random = Button(
            self.button_color,
            self.screen_width//4 + self.constants.MENU_OFFSET,
            self.screen_height//2 + 60,
            button_width, button_height, "AI vs Random"
        )
        self.button_ai_ai = Button(
            self.button_color,
            self.screen_width//4 + self.constants.MENU_OFFSET,
            self.screen_height//2 - 20,
            button_width, button_height, "AI vs AI"
        )
        
        # Load background and logo images
        try:
            self.image = p.transform.scale(
                p.image.load("assets/images/menu/main_logo.png"), 
                (int(self.screen_width//3 + self.constants.SIDE_SCREEN), int(self.screen_height//2.5))
            )
            self.background = p.transform.scale(
                p.image.load("assets/images/menu/background.jpg"),
                (self.screen_width + self.constants.SIDE_SCREEN, self.screen_height + 5)
            )
        except:
            # Create placeholder graphics if images not found
            self.image = p.Surface((200, 100))
            self.image.fill(self.constants.WHITE)
            self.background = p.Surface((self.screen_width + self.constants.SIDE_SCREEN, self.screen_height))
            self.background.fill(self.constants.DIM_BLUE)

    def draw_main_menu(self):
        """Display the main menu"""
        p.init()
        running = True
        self.screen.fill(self.constants.DARK_BLUE)
        
        while running:
            self.screen.blit(self.background, p.Rect(0, 0, self.screen_width, self.screen_height))
            self.screen.blit(self.image, (
                (self.constants.WIDTH + self.constants.SIDE_SCREEN - self.image.get_width())//2, 25
            ))
            
            for event in p.event.get():
                if event.type == p.QUIT:
                    running = False
                    p.quit()
                elif event.type == p.MOUSEBUTTONDOWN:
                    location = p.mouse.get_pos()
                    if self.button_play.is_over(location):
                        running = False
                        self.draw_play_menu()
                    elif self.button_rules.is_over(location):
                        running = False
                        self.draw_rules_menu()
                    elif self.button_controls.is_over(location):
                        running = False
                        self.draw_controls_menu()
                        
            # Draw buttons
            self.button_play.draw(self.screen)
            self.button_rules.draw(self.screen)
            self.button_controls.draw(self.screen)
            p.display.flip()

    def draw_play_menu(self):
        """Display play options menu"""
        p.display.init()
        running = True
        
        while running:
            self.screen.fill(self.constants.DARK_BLUE)
            self.screen.blit(self.background, p.Rect(0, 0, self.screen_width, self.screen_height))
            self.screen.blit(self.image, (
                (self.constants.WIDTH + self.constants.SIDE_SCREEN - self.image.get_width())//2, 25
            ))

            for event in p.event.get():
                if event.type == p.QUIT:
                    running = False
                    p.display.quit()
                elif event.type == p.KEYDOWN:
                    if event.key == p.K_ESCAPE:
                        running = False
                        self.draw_main_menu()
                elif event.type == p.MOUSEBUTTONDOWN:
                    location = p.mouse.get_pos()
                    if self.button_pvp.is_over(location):
                        self.controller.set_player_vs_player()
                        running = False
                        self.view.main()
                        p.display.quit()
                    elif self.button_pva.is_over(location):
                        running = False
                        self.draw_difficulty_menu(True)
                    elif self.button_ai_menu.is_over(location):
                        running = False
                        self.draw_difficulty_menu(False)
            
            # Draw play menu buttons
            self.button_pvp.draw(self.screen)
            self.button_pva.draw(self.screen)
            self.button_ai_menu.draw(self.screen)
            p.display.flip()

    def draw_difficulty_menu(self, is_human_vs_ai: bool):
        """Display AI difficulty selection"""
        p.display.init()
        running = True
        
        while running:
            self.screen.fill(self.constants.DARK_BLUE)
            self.screen.blit(self.background, p.Rect(0, 0, self.screen_width, self.screen_height))
            self.screen.blit(self.image, (
                (self.constants.WIDTH + self.constants.SIDE_SCREEN - self.image.get_width())//2, 25
            ))
            
            for event in p.event.get():
                if event.type == p.QUIT:
                    running = False
                    p.display.quit()
                elif event.type == p.KEYDOWN:
                    if event.key == p.K_ESCAPE:
                        running = False
                        self.draw_play_menu()
                elif event.type == p.MOUSEBUTTONDOWN:
                    location = p.mouse.get_pos()
                    if self.button_easy.is_over(location):
                        self.controller.set_ai_difficulty(1)
                        running = False
                        if is_human_vs_ai:
                            self.draw_ai_color_menu()
                        else:
                            self.draw_ai_vs_ai_menu()
                    elif self.button_normal.is_over(location):
                        self.controller.set_ai_difficulty(2)
                        running = False
                        if is_human_vs_ai:
                            self.draw_ai_color_menu()
                        else:
                            self.draw_ai_vs_ai_menu()
                    elif self.button_hard.is_over(location):
                        self.controller.set_ai_difficulty(3)
                        running = False
                        if is_human_vs_ai:
                            self.draw_ai_color_menu()
                        else:
                            self.draw_ai_vs_ai_menu()
            
            # Draw difficulty buttons
            self.button_easy.draw(self.screen)
            self.button_normal.draw(self.screen)
            self.button_hard.draw(self.screen)
            p.display.flip()

    def draw_ai_color_menu(self):
        """Let player choose AI color"""
        p.display.init()
        running = True
        
        while running:
            self.screen.fill(self.constants.DARK_BLUE)
            self.screen.blit(self.background, p.Rect(0, 0, self.screen_width, self.screen_height))
            self.screen.blit(self.image, (
                (self.constants.WIDTH + self.constants.SIDE_SCREEN - self.image.get_width())//2, 25
            ))
            
            for event in p.event.get():
                if event.type == p.QUIT:
                    running = False
                    p.display.quit()
                elif event.type == p.KEYDOWN:
                    if event.key == p.K_ESCAPE:
                        running = False
                        self.draw_play_menu()
                elif event.type == p.MOUSEBUTTONDOWN:
                    location = p.mouse.get_pos()
                    if self.button_ai_black.is_over(location):
                        self.controller.set_ai_black()
                        running = False
                        self.view.main()
                        p.display.quit()
                    elif self.button_ai_white.is_over(location):
                        self.controller.set_ai_white()
                        running = False
                        self.view.main()
                        p.display.quit()
            
            self.button_ai_black.draw(self.screen)
            self.button_ai_white.draw(self.screen)
            p.display.flip()

    def draw_ai_vs_ai_menu(self):
        """AI vs AI options"""
        p.display.init()
        running = True
        
        while running:
            self.screen.fill(self.constants.DARK_BLUE)
            self.screen.blit(self.background, p.Rect(0, 0, self.screen_width, self.screen_height))
            self.screen.blit(self.image, (
                (self.constants.WIDTH + self.constants.SIDE_SCREEN - self.image.get_width())//2, 25
            ))
            
            for event in p.event.get():
                if event.type == p.QUIT:
                    running = False
                    p.display.quit()
                elif event.type == p.KEYDOWN:
                    if event.key == p.K_ESCAPE:
                        running = False
                        self.draw_play_menu()
                elif event.type == p.MOUSEBUTTONDOWN:
                    location = p.mouse.get_pos()
                    if self.button_ai_random.is_over(location):
                        self.controller.set_random_vs_ai()
                        running = False
                        self.view.main()
                        p.display.quit()
                    elif self.button_ai_ai.is_over(location):
                        self.controller.set_ai_vs_ai()
                        running = False
                        self.view.main()
                        p.display.quit()
            
            self.button_ai_random.draw(self.screen)
            self.button_ai_ai.draw(self.screen)
            p.display.flip()

    def draw_rules_menu(self):
        """Display chess rules"""
        p.init()
        running = True
        font = p.font.SysFont('Arial', 24)
        flag = True

        
        while running:
            self.screen.fill(self.constants.DARK_BLUE)
            if flag:
                rules_text = [
                    "CHESS RULES",
                    "",
                    "OBJECTIVE: Checkmate the opponent's king",
                    "",
                    "PIECE MOVEMENTS:",
                    "• Pawn: Forward 1, or 2 on first move",
                    "• Rook: Horizontal and vertical lines", 
                    "• Bishop: Diagonal lines",
                    "• Knight: L-shape (2+1 squares)",
                    "• Queen: Any direction, any distance",
                    "• King: One square in any direction",
                    "",
                    "Click for next page"
                    ""
                ]
            else:
                rules_text=[
                "SPECIAL MOVES:",
                "• Castling: King and rook move together",
                "• En passant: Pawn captures sideways",
                "• Promotion: Pawn reaches end of board",
                "",
                "Press ESCAPE to return to menu"]
            
            for event in p.event.get():
                if event.type == p.QUIT:
                    running = False
                    p.quit()
                elif event.type == p.KEYDOWN:
                    if event.key == p.K_ESCAPE:
                        running = False
                        self.draw_main_menu()
                elif event.type == p.MOUSEBUTTONDOWN:
                    flag = not flag
            
            # Draw rules text
            y_offset = 50
            for line in rules_text:
                if line.startswith("CHESS RULES"):
                    text_surface = p.font.SysFont('Arial', 32, bold=True).render(line, True, self.constants.WHITE)
                elif line.startswith(("OBJECTIVE:", "PIECE MOVEMENTS:", "SPECIAL MOVES:")):
                    text_surface = p.font.SysFont('Arial', 26, bold=True).render(line, True, self.constants.WHITE)
                else:
                    text_surface = font.render(line, True, self.constants.WHITE)
                
                self.screen.blit(text_surface, (50, y_offset))
                y_offset += 30
            
            p.display.flip()

    def draw_controls_menu(self):
        """Display game controls"""
        p.display.init()
        running = True
        font = p.font.SysFont('Arial', 24)
        flag = True

        
        while running:
            self.screen.fill(self.constants.WHITE)
            if flag:
                controls_text = [
                    "GAME CONTROLS",
                    "",
                    "MOUSE:",
                    "• Click to select piece",
                    "• Click destination to move",
                    "• Click save/load buttons",
                    "",
                    "KEYBOARD:",
                    "• Z - Undo last move",
                    "• R - Reset game", 
                    "• ESC - Return to menu",
                    "",
                    "Click for next page"
                    ]
            else:
                controls_text= [
                "PAWN PROMOTION:",
                "• Click Q, R, B, or N when prompted",
                "",
                "Press ESCAPE to return to menu"
                    ]
            
            for event in p.event.get():
                if event.type == p.QUIT:
                    running = False
                    p.display.quit()
                elif event.type == p.KEYDOWN:
                    if event.key == p.K_ESCAPE:
                        running = False
                        self.draw_main_menu()
                elif event.type == p.MOUSEBUTTONDOWN:
                    flag = not flag
            
            # Draw controls text
            y_offset = 50
            for line in controls_text:
                if line.startswith("GAME CONTROLS"):
                    text_surface = p.font.SysFont('Arial', 32, bold=True).render(line, True, self.constants.BLACK)
                elif line.startswith(("MOUSE:", "KEYBOARD:", "PAWN PROMOTION:")):
                    text_surface = p.font.SysFont('Arial', 26, bold=True).render(line, True, self.constants.BLACK)
                else:
                    text_surface = font.render(line, True, self.constants.BLACK)
                
                self.screen.blit(text_surface, (50, y_offset))
                y_offset += 30
            
            p.display.flip()