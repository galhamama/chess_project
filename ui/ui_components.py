"""Reusable UI components"""

import pygame as p

class Button:
    def __init__(self, color, x, y, width, height, text=''):
        """Button class for UI elements"""
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

    def draw(self, win, outline=None):
        """Draw the button on the screen"""
        if outline:
            p.draw.rect(win, outline, (self.x-2, self.y-2, self.width+4, self.height+4), 0)
            
        p.draw.rect(win, self.color, (self.x, self.y, self.width, self.height), 0)
        
        if self.text != '':
            font = p.font.SysFont('garamond', 40)
            text = font.render(self.text, 1, (255, 255, 255))
            win.blit(text, (self.x + (self.width/2 - text.get_width()/2), 
                           self.y + (self.height/2 - text.get_height()/2)))

    def is_over(self, pos):
        """Check if position is over the button"""
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True
        return False