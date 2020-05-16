import pygame as pg
from settings import *

class WSPELL(pg.sprite.Sprite):
    """
    Parent class for spells
    """
    name = "NAMELESS"
    def __init__(self, game, color=GREEN):
        self.groups = game.spells
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(color)
        self.rect = self.image.get_rect()

        # hide the spell under the player
        self.x = game.player.x
        self.y = game.player.y

        self.gx = 0
        self.gy = 0
        self.rect.x = self.x * TILESIZE
        self.rect.y = self.y * TILESIZE
        
        # filled out by child class
        self.is_firing = False
        self.velocity = None
        self.elements = []  
        self.inspect_message = "Its a spell of some kind"
        self.interact_message = "Not sure what I could do with that..."
    
    def __str__(self):
        return self.name
    
    def update(self):
        if self.is_firing:
            # use the global position of the player to decide what to draw
            cur_g_x = self.game.player.global_x
            cur_g_y = self.game.player.global_y

            # need to massage the indexes so that (xmin, ymin) is (0, 0) on the view
            xmin = cur_g_x - 6
            xmax = cur_g_x + 10
            ymin = cur_g_y - 6
            ymax = cur_g_y + 10

            # if we are out of sight, despawn
            if self.gx < xmin or self.gx > xmax or self.gy < ymin or self.gy > ymax:
                super().kill()
            
            # TODO update location
    
    def inspect(self):
        return self.inspect_message

    def interact(self, player):
        if player.equipped_spell == self:
            return "I already have that spell equipped"
        else:
            player.equipped_spell = self
            return f"I equipped the spell '{self.name}'"

class Fire(WSPELL):
    name = "Fire Ball"
    def __init__(self, game):
        super().__init__(game, color=RED)
        self.elements.append("fire")
        self.inspect_message = "a Fire Ball spell"


            