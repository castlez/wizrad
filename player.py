import pygame as pg
from settings import *
import traceback

class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()

        # position on the screen
        self.x = x
        self.y = y
        
        # position in the level
        self.global_x = 0
        self.global_y = 0
        self.still = True

        self.collisions = False

        # game statue
        self.spells = []
        self.equipped_spell = None
        self.is_firing = False
    
    def inspect(self):
        return "I am badass, swagass, Wizrad"

    def update_global_position(self, x, y):
        self.global_x = x
        self.global_y = y

    def move(self, dx=0, dy=0):
        blocked = self.check_collision(dx, dy)
        if not blocked:
            self.global_x += dx
            self.global_y += dy
            self.still = False

    def update(self):
        self.rect.x = self.x * TILESIZE
        self.rect.y = self.y * TILESIZE
    
    def check_collision(self, dx, dy):
        new_x = self.x + dx
        new_y = self.y + dy
        blocked = False
        for wall in self.game.walls:
            if new_x == wall.x and new_y == wall.y and self.collisions:
                blocked = True
        return blocked
    
    def inspect_space(self, mouse_pos):
        message = ""
        for sprite in self.game.all_sprites:
            try:
                if sprite.rect.collidepoint(mouse_pos):
                    message = sprite.inspect()
                    break
            except Exception as e:
                self.game.log.info(e)
                continue
        if message != "" and message != None:
            self.game.log.info(message)
        else:
            self.game.log.info("Its the floor. Im looking at the floor... "
                               "Maybe i should look at other things")

    def interact_space(self, mouse_pos):        
        message = ""
        for sprite in self.game.all_sprites:
            try:
                if sprite.rect.collidepoint(mouse_pos):
                    message = sprite.interact(self)
                    break
            except Exception as e:
                self.game.log.info(e)
                continue
        if message != "" and message != None:
            self.game.log.info(message)
        else:
            self.game.log.info("Its the floor. Im looking at the floor... "
                            "Maybe i should look at other things")
    
    def has_element(self, element):
        has_ele = False
        for spell in self.spells:
            if element in spell.elements:
                has_ele = True
        return has_ele
    
    def get_spells(self):
        return [s.name for s in self.spells]
    
    def add_spell(self, spell):
        self.spells.append(spell)
        if self.equipped_spell == None:
                self.equipped_spell = spell(self.game)
    
    def fire_spell(self, mouse_pos):
        if self.equipped_spell:
            self.is_firing = True
            self.equipped_spell.rect.x = mouse_pos[0]
            self.equipped_spell.rect.y = mouse_pos[1]
