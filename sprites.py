import pygame as pg
from spells import *
from settings import *


class WSPRITE(pg.sprite.Sprite):
    """
    Parent class for all sprites but the player
    (you are special ;) )

    oh and the log window (because it doesnt move)

    also spells have their own parent
    """
    def __init__(self, game, x, y, gx, gy, group, color=GREEN):
        self.groups = game.all_sprites, group
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.gx = gx
        self.gy = gy
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE
        self.inspect_message = "I have no idea what that is..."
        self.interact_message = "Not sure what I could do with that..."
    
    def update(self):
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
    
    def inspect(self):
        return self.inspect_message
    
    def interact(self, player):
        return self.interact_message

class Wall(WSPRITE):
    def __init__(self, game, x, y, gx, gy):
        super().__init__(game, x, y, gx, gy, game.walls, color=LIGHTGREY)
        self.inspect_message = "I think its.. well, it might be.. yeah that is! Its a wall!"
    
    # def inspect(self):
    #     return "I think its.. well, it might be.. yeah that is! Its a wall!"
    
    def update(self):
        super().update()

class BurningPile(WSPRITE):
    """
    These give you fire
    """
    def __init__(self, game, x, y, gx, gy):
        super().__init__(game, x, y, gx, gy, game.inters, color=RED)
        self.inspect_message = "A magic fire, i better watch out. Hmm.. "\
                               "its interesting (right click to study)"
    
    def update(self):
        super().update()
    
    def interact(self, player):
        if player.has_element("fire"):
            return "I already know how to wield fire magic"
        else:
            player.add_spell(Fire)
            return "I studied the pile and learned the secrets of fire magic!"
            

class Skeleton(WSPRITE):
    def __init__(self, game, x, y, gx, gy):
        super().__init__(game, x, y, gx, gy, game.inters, color=RED)
        self.inspect_message = "An animated skeleton. A good fireball should do the trick."
    
    def update(self):
        super().update()