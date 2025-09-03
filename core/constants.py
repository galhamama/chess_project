"""Game constants and configuration values"""

class ConstantValues:
    def __init__(self):
        """Constants for the chess game"""
        
        # Screen settings
        self.WIDTH: int = 512
        self.HEIGHT: int = self.WIDTH 
        self.SIDE_SCREEN = 200
        self.MENU_OFFSET = self.SIDE_SCREEN / 2
        self.DIMENSION: int = 8
        self.SQ_SIZE: int = self.HEIGHT // self.DIMENSION
        self.MAX_FPS: int = 15
        self.IMAGE: dict = {}
        
        # Board representation
        self.EMPTY_POSITION = "--"
        self.WHITE_PLAYER = 'w'
        self.BLACK_PLAYER = 'b'
        
        # Colors
        self.LIGHT_GRAY = (126, 135, 152)
        self.DARK_BLUE = (43, 50, 64)
        self.DIM_BLUE = (21, 28, 41)
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.DARK_GRAY = (36, 36, 36)

