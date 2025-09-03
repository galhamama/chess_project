"""Main entry point for the chess game"""

if __name__ == "__main__":
    from ui.game_view import GameView
    from ui.menu_system import MainMenu
    
    game = GameView()
    menu = MainMenu(game)
    menu.draw_main_menu()