'''UI'''
import pygame as pg

pg.init()
COLOR = pg.Color('white')
FONT = pg.font.SysFont("Segoe UI", 20)


class Label:

    def __init__(self, x, y, text=""):
        self.color = COLOR
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False
        self.x = x
        self.y = y

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.x, self.y))
