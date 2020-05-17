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

        # determine the shot directions, 
        # first get mouse position in tiles
        # then normalize to -1, 0, 1 for x and y
        mx = int(mouse_pos[0]/TILESIZE)
        my = int(mouse_pos[1]/TILESIZE)
        dx, dy = self.normalize_quards(mx, my)
        self.target_pos = [dx, dy]
        
        # time tracking to change spell speed
        self.cur_interval = time.time()
    
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
        # first check if the player moved
        # and adjust for the new viewport
        dx = self.game.player.dx
        dy = self.game.player.dy
        tx = self.target_pos[0]
        ty = self.target_pos[1]
        tx -= dx
        ty -= dy
        print("----")
        print(f"self.target_pos = {self.target_pos}")
        print(f"dx,dy={dx},{dy}")
        print(f"tx,ty={tx},{ty}")
        print("----")

        # update the global position and ensure we're still in view
        self.gx += self.target_pos[0]
        self.gy += self.target_pos[1]
        if not self.game.object_in_view(self.gx, self.gy):
            super().kill()
            self.game.player.is_firing = False
        else:
            # update rect location
            self.rect.x += tx * TILESIZE
            self.rect.y += ty * TILESIZE
    
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


            