import pygame as pg
from settings import *

class LogWindow(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        # position should be fixed at the bottom
        self.image = pg.Surface((TILESIZE*8, TILESIZE*3))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE * 8
        self.rect.y = y * TILESIZE * 2

        # keep track of the log lines
        self.log = ["Welcome to Wizrad!"]
        self.current_place = 0
        self.current_display = []
    
    def update_place(self, change):
        self.current_place += change
    
    def info(self, message):
        self.log.append(f"i:{message}")
    
    def update(self):
        # get the last VIS_LOG_LINES lines into draw_lines
        draw_lines = []
        if len(self.log) < 3:
            draw_lines = self.log
        else:
            draw_lines = self.log[-3::]
        
        # draw the log TODO
        if draw_lines != self.current_display:
            self.current_display = draw_lines
            print("----------")
            for line in draw_lines:
                tag = line[:1]
                message = line[2:]
                if tag == "i":
                    print(f"INFO: {message}")
                elif tag == "e":
                    print(f"EROR: {message}")
                else:
                    print(line)
            print("----------")

            
        

