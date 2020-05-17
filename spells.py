import pygame as pg
from settings import *
import time

class WSPELL(pg.sprite.Sprite):
    """
    Parent class for spells
    """
    name = "NAMELESS"
    def __init__(self, game, mouse_pos, color=GREEN):
        self.groups = game.spells
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(color)
        self.rect = self.image.get_rect()

        # hide the spell under the player
        self.x = game.player.x
        self.y = game.player.y
        self.pos = pg.math.Vector2(self.x, self.y)

        self.gx = game.player.global_x
        self.gy = game.player.global_y
        
        # filled out by child class
        self.elements = []  
        self.inspect_message = "Its a spell of some kind"
        self.interact_message = "Not sure what I could do with that..."

        # shooting
        self.vel = None
        self.shot_start = None
        self.rect.x = self.x * TILESIZE
        self.rect.y = self.y * TILESIZE

        # determine the shot directions, first get mouse position in tiles
        print("------")
        mx = int(mouse_pos[0]/TILESIZE)
        my = int(mouse_pos[1]/TILESIZE)
        print(f"(mx, my) = ({mx}, {my})")

        # finally normalize to -1, 0, 1
        dx, dy = self.normalize_quards(mx, my)
        print(f"(dx, dy) = ({dx}, {dy})")
        
        print("------")

        # self.target_pos = [dx, dy]
        self.target_pos = [dx, dy]
    
    def normalize_quards(self, x, y):
        """
        this is a very smol brain function
        |(-1,-1)|0,-1)|(1,-1)|
        |(-1,0) |playr|(1,0) |
        |(-1,1) |(0,1)|(1,1) |
        """
        rx = 0
        ry = 0

        if x == PLAYER_X:
            rx = 0
        elif x > PLAYER_X:
            rx = 1
        elif x < PLAYER_X:
            rx = -1

        if y == PLAYER_Y:
            ry = 0
        elif y > PLAYER_Y:
            ry = 1
        elif y < PLAYER_Y:
            ry = -1
        return rx, ry

    
    def __str__(self):
        return self.name
    
    def update(self):
        self.rect.x += self.target_pos[0] * TILESIZE
        self.rect.y += self.target_pos[1] * TILESIZE
            
    
    # def update(self):
    #     print("---- update ----")
    #     delta = self.pos + self.target_pos
    #     direction = delta.normalize()
    #     print(f"normy: {direction}")
    #     self.vel = direction * 6
    #     #self.vel = pg.math.Vector2(int(self.vel[0]), int(self.vel[1]))
    #     self.vel = pg.math.Vector2(1, 2)

    #     self.shot_start = time.time()
    #     print(f"updating from {self.pos} to {self.pos + self.vel}")
    #     # use the global position of the player to decide what to draw
    #     cur_g_x = self.game.player.global_x
    #     cur_g_y = self.game.player.global_y

    #     xmin = cur_g_x - 6
    #     xmax = cur_g_x + 10
    #     ymin = cur_g_y - 6
    #     ymax = cur_g_y + 10
    #     self.gx += self.vel[0]
    #     self.gy += self.vel[1]
    #     print(f"gx,gy = ({self.gx}, {self.gy})")

    #     # if we are out of sight, despawn
    #     if self.gx < xmin or self.gx > xmax or self.gy < ymin or self.gy > ymax:
    #         print(f"view: (xmin{xmin}, xmax{xmax}), (ymin{ymin}, ymax{ymax})")
    #         print("killing")
    #         super().kill()

    #     # update location
    #     # self.pos = self.pos + self.vel
    #     # print(f"new vel: {self.vel}")
    #     newx = self.rect.x
    #     newy = self.rect.y + 1
    #     self.rect.x = newx * TILESIZE
    #     self.rect.x = newy * TILESIZE

    #     print("--------")
    
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
    def __init__(self, game, target_pos):
        super().__init__(game, target_pos, color=RED)
        self.elements.append("fire")
        self.inspect_message = "a Fire Ball spell"


            