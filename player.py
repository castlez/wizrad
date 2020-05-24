import pygame as pg
from settings import *
import os
import traceback

class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.playerg
        # self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(YELLOW)
        # self.image = pg.image.load(os.path.join("assets", "wiz_up.png"))
        # self.image = pg.transform.scale(self.image, (TILESIZE, TILESIZE))
        # TODO: use rotozoom to rotate 
        # self.image = pg.Surface(self.image.get_size()).convert_alpha()
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.state = PlayerState()
        self.name = "Player"

        # position on the screen with current change
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        
        # position in the level
        self.gx = 0
        self.gy = 0
        self.still = True

        self.collisions = True

        # game status
        self.spells = []
        self.active_spells = []
        self.equipped_spell = None
        self.is_firing = False
        self.equipped_item = None

    def drawt(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))
    
    def take_damage(self, source, amount):
        if GODMODE:
            self.game.log.info(f"Woulda taken {amount} dmg if not for godmode")
            return
        self.state.Health.value -= amount
        self.game.log.info(f"Hit by {source.name} for {amount} damage")
        self.game.log.info(f"Remaining health: {self.state.Health.value}")
        if self.state.Health.value <= 0:
            self.state.alive = False
    
    def inspect(self):
        return "I am badass, swagass, Wizrad"

    def update_global_position(self, x, y):
        self.gx = x
        self.gy = y

    def move(self, dx=0, dy=0):
        blocked = self.check_collision(dx, dy)
        if not blocked:
            self.dx = dx
            self.dy = dy
            self.gx += dx
            self.gy += dy
            self.still = False

    def update(self):
        self.check_spells()
        self.rect.x = self.x * TILESIZE
        self.rect.y = self.y * TILESIZE
    
    def check_spells(self):
        for i, spell in enumerate(self.active_spells):
            if not spell.active:
                spell.kill()
                del self.active_spells[i]
    
    def is_moving(self):
        return self.dx != 0 and self.dy != 0
    
    def check_collision(self, dx, dy):
        new_x = self.x + dx
        new_y = self.y + dy
        blocked = False
        for sprite in self.game.all_sprites:
            if new_x == sprite.x and new_y == sprite.y and sprite.blocking:
                blocked = True
        # blocked if we hit something and collisions are on
        is_blocked = blocked and not self.game.godmode
        return is_blocked
    
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
        if message == "" or message == None:
            message = "Its the floor. Im looking at the floor... "\
                      "Maybe i should look at other things"
        self.game.log.info(message)

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
        if message == "" or message == None:
            message = "Not much to do with the floor really.."
        self.game.log.info(message)
    
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
        if not self.equipped_spell:
            self.equipped_spell = spell
    
    def fire_spell(self, mouse_pos):
        if self.equipped_spell:
            self.is_firing = True
            spell = self.equipped_spell(self.game, mouse_pos)
            self.active_spells.append(spell)
    
    def get_item(self, item):
        if len(self.state.inventory) + 1 <= self.state.Strength.value:
            self.state.inventory.append(item)
            if not self.equipped_item:
                self.equipped_item = item
            return True
        else:
            self.game.log.info("I can't carry any more :(")
            return False
    
    def use_item(self):
        if self.equipped_item:
            self.equipped_item.use()
            # if its consumable, remove it after use
            if self.equipped_item.consumable:
                self.state.inventory.remove(self.equipped_item)
                # equip the next item if there is one, or empty hands
                if len(self.state.inventory) > 0:
                    self.equipped_item = self.state.inventory[0]
                else:
                    self.equipped_item = None

    def heal_hp(self, amount_pcnt):
        max_health = self.state.Health.max_health
        cur_health = self.state.Health.value
        gained = int(max_health * amount_pcnt)
        if cur_health + gained <= max_health:
            new_health = cur_health + gained
        else:
            new_health = max_health
        new_health = int(new_health)
        self.state.Health.value = new_health
    
    def get_stats(self):
        return self.state.get_stats()

class PlayerState:
    known_spells = None
    alive = True
    inventory = []

    # these absurd classes are because i need
    # to be able to display contextual information
    # in menues about these stats (what they do)
    class Health:
        name = "Health"
        max_health = PLAYER_START_HEALTH
        value = PLAYER_START_HEALTH
        description = "My current health"
        changed = False
        @classmethod
        def inspect(cls):
            return cls.description
        @classmethod
        def set(cls, value):
            cls.value = value
        @classmethod
        def is_changed(cls):
            changed = cls.changed
            cls.changed = False
            return changed
    class Strength:
        name = "Strength"
        value = PLAYER_START_STR
        description = "How many items I can carry"
        changed = False
        @classmethod
        def inspect(cls):
            return cls.description
        @classmethod
        def set(cls, value):
            cls.value = value
        @classmethod
        def is_changed(cls):
            changed = cls.changed
            cls.changed = False
            return changed
    class Constitution:
        name = "Constitution"
        value = PLAYER_START_CON
        description = "My max hitpoints (at full health)"
        changed = False
        @classmethod
        def inspect(cls):
            return cls.description
        @classmethod
        def set(cls, value):
            cls.value = value
        @classmethod
        def is_changed(cls):
            changed = cls.changed
            cls.changed = False
            return changed
    class Intelligence:
        name = "Intelligence"
        value = PLAYER_START_INT
        description = "How many spells I can know"
        changed = False
        @classmethod
        def inspect(cls):
            return cls.description
        @classmethod
        def set(cls, value):
            cls.value = value
        @classmethod
        def is_changed(cls):
            changed = cls.changed
            cls.changed = False
            return changed
    
    @classmethod
    def get_stats(cls):
        return [cls.Health, cls.Strength, cls.Constitution, cls.Intelligence]
    
    @classmethod
    def stats_changed(cls):
        return cls.Strength.is_changed() or cls.Constitution.is_changed() or cls.Intelligence.is_changed()


    
