import pygame as pg
from settings import *
import os

class WSCREEN(pg.sprite.Sprite):
    """
    Parent class for non viewport screens
    inventory
    more?
    """
    def __init__(self, game, x, y):
        self.groups = game.screens
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.inspect_message = "A Screen for lookin..."
        self.name = "AScreen"

        # position should be fixed at the bottom
        self.image = pg.Surface((WIDTH, LOG_Y))
        self.image.fill(BLACK)
        self.x = S_X
        self.y = S_Y
        self.cur_x = self.x
        self.cur_y = self.y
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

        # keep track of the visible lines
        self.current_place = 0
        # [[inventory], [spells]]
        self.current_display = [[],[]]

        # text stuff
        fonts = pg.font.get_fonts()
        self.font = pg.font.SysFont(fonts[0], S_TEXT_SIZE)
    
    def update(self):
        pass

    def drawt(self, screen):
        pass

class Inventory(WSCREEN):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
    
    def update(self):
        """
        check the players inventory and update
        current display
        """
        # player inventory
        cur_inven = self.game.player.state.inventory
        if len(cur_inven) != len(self.current_display[0]):
            self.current_display[0] = []
            for item in cur_inven:
                self.current_display[0].append(item)
        # spells
        cur_spells = self.game.player.spells
        if len(cur_spells) != len(self.current_display[1]):
            self.current_display[1] = []
            for spell in cur_spells:
                self.current_display[1].append(spell)
    
    def draw_text_line(self, screen, text, color=WHITE):
        text = self.font.render(text, True, color, (0, 0, 0))
        screen.blit(text, (self.cur_x, self.cur_y))
        self.cur_y += S_LINE_DIST
    
    def drawt(self, screen):

        # draw the black backdrop
        screen.blit(self.image, (self.x, self.y))

        # inventory header
        self.draw_text_line(screen, "Inventory")
        self.draw_text_line(screen, "---------")

        # line for each item
        for item in self.current_display[0]:
            if item == self.game.player.equipped_item:
                self.draw_text_line(screen, item.name, color=RED)
            else:
                self.draw_text_line(screen, item.name)
        
        # reset cur_x and cur_y for spells next
        self.cur_x = self.x + WIDTH/2
        self.cur_y = self.y

        # spells header
        self.draw_text_line(screen, "Spells")
        self.draw_text_line(screen, "------")

        # line for each spell
        for spell in self.current_display[1]:
            if spell == self.game.player.equipped_spell:
                self.draw_text_line(screen, spell.name, color=RED)
            else:
                self.draw_text_line(screen, spell.name)
        
        # reset cur_x and cur_y completely
        self.cur_x = self.x
        self.cur_y = self.y




        

