import random
import pygame as pg
from settings import *
import time

class WSPELL(pg.sprite.Sprite):
    """
    Parent class for spells
    """
    name = "NAMELESS"
    def __init__(self, game, mouse_pos, color=GREEN):
        self.groups = game.all_sprites, game.spells
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((SPELL_SIZE, SPELL_SIZE))
        # self.image = pg.transform.rotozoom(self.image, 0, 0.5)
        self.image.fill(color)
        self.rect = self.image.get_rect()

        # hide the spell under the player
        self.x = game.player.x
        self.y = game.player.y
        self.pos = pg.math.Vector2(self.x, self.y)

        self.gx = game.player.gx
        self.gy = game.player.gy
        self.moved = 0  # so the player doesnt die when they cast
        
        # filled out by child class
        self.elements = []  
        self.inspect_message = "Its a spell of some kind"
        self.interact_message = "Not sure what I could do with that..."
        self.effect = None

        # shooting
        self.vel = None
        self.shot_start = None
        
        # determine the shot directions, 
        # first get mouse position in tiles
        # then normalize to -1, 0, 1 for x and y
        mx = int(mouse_pos[0]/TILESIZE)
        my = int(mouse_pos[1]/TILESIZE)
        dx, dy = self.normalize_quards(mx, my)
        self.target_pos = [dx, dy]
        self.rect.x = self.x * TILESIZE
        self.rect.y = self.y * TILESIZE

        # self.check_hit()
        
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
    
    def get_next_dx(self):
        dx = self.game.player.dx
        dy = self.game.player.dy
        tx = self.target_pos[0]
        ty = self.target_pos[1]
        tx -= dx
        ty -= dy

        return tx, ty
    
    def update(self):
        # first check if the player moved
        # and adjust for the new viewport
        tx, ty = self.get_next_dx()

        # update the global position and ensure we're still in view
        # self.gx += self.target_pos[0]
        # self.gy += self.target_pos[1]
        self.gx += tx
        self.gy += ty
        if not self.game.object_in_view(self.gx, self.gy):
            super().kill()
            self.game.player.is_firing = False
        else:
            # update loc
            # x, y = self.game.current_floor.get_local_pos(self.gx, self.gy)
            self.x += tx
            self.y += ty
            self.rect.x += tx * TILESIZE
            self.rect.y += ty * TILESIZE
            # check if you hit something
            self.check_hit()
    
    def draw(self, screen):
        print(f"|{self.rect.x},{self.rect.y}|{SPELL_SIZE}|{self.rect.x + SPELL_SIZE}")
        draw_x = self.rect.x
        draw_y = self.rect.y + int(SPELL_SIZE/4)
        screen.blit(self.rect, (draw_x, draw_y))
    
    def check_hit(self):
        for sprite in self.game.all_sprites:
            try:
                if sprite.x == self.x and sprite.y == self.y and sprite != self:
                    self.hit(sprite)
            except:
                pass

    def inspect(self):
        return self.inspect_message

    def interact(self, player):
        if player.equipped_spell == self:
            return "I already have that spell equipped"
        else:
            player.equipped_spell = self
            return f"I equipped the spell '{self.name}'"
    
    def hit(self, target):
        """
        Anything that can hit something has this!
        what happens when this hits something
        """
        print("WRONG ONE")
        return False
    
    def kill(self):
        super().kill()

class Fire(WSPELL):
    name = "Fire Ball"
    def __init__(self, game, target_pos):
        super().__init__(game, target_pos, color=RED)
        self.elements.append("fire")
        self.inspect_message = "a Fire Ball spell"
    
    def hit(self, target):
        try:
            if self.rect.colliderect(target.rect):
                target.take_damage(random.randint(FDAMAGE_RANGE[0], FDAMAGE_RANGE[1]))
                super().kill()
                return True
        except Exception as e:
            print(e)
            
        return False




            