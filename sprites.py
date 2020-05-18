import pygame as pg
from spells import *
from settings import *
import math


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
        self.dx = 0
        self.dy = 0
        self.gx = gx
        self.gy = gy
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE
        self.inspect_message = "I have no idea what that is..."
        self.interact_message = "Not sure what I could do with that..."

        self.blocking = True
    
    def update(self):
        if not self.game.object_in_view(self.gx, self.gy):
            super().kill()
    
    def inspect(self):
        return self.inspect_message
    
    def interact(self, player):
        return self.interact_message
    
    def kill(self):
        super().kill()

class Wall(WSPRITE):
    def __init__(self, game, x, y, gx, gy):
        super().__init__(game, x, y, gx, gy, game.walls, color=LIGHTGREY)
        self.inspect_message = "I think its.. well, it might be.. yeah that is! Its a wall!"
        self.blocking = True
        self.name = "Wall"
    
    def inspect(self):
        return "I think its.. well, it might be.. yeah that is! Its a wall!"
    
    def update(self):
        super().update()
    
    def take_damage(self, amount):
        print("wall hit")
        self.game.log.info(f"You would have done {amount} damage to the wall, if that was possible.")

class BurningPile(WSPRITE):
    """
    These give you fire
    """
    def __init__(self, game, x, y, gx, gy):
        super().__init__(game, x, y, gx, gy, game.inters, color=RED)
        self.inspect_message = "A magic fire, i better watch out. Hmm.. "\
                               "its interesting (right click to study)"
        self.name = "BurningPile"
        self.visible = True
        self.start_pos = (gx, gy)
        self.set_sign(FIRE + SPAWNED)
        
    
    def update(self):
        if self.visible:
            try:
                x, y = self.get_local_pos() 
                self.x = x - self.game.player.dx
                self.y = y - self.game.player.dy
            except Exception as e:
                print(e)
            self.rect.x = self.x * TILESIZE
            self.rect.y = self.y * TILESIZE
    
    def get_local_pos(self):
        return self.game.current_floor.get_local_pos(self.gx, self.gy)
    
    def draw(self, screen):
        if self.visible:
            screen.blit(self.rect, (self.rect.x, self.rect.y))
    
    def interact(self, player):
        if player.has_element("fire"):
            return "I already know how to wield fire magic"
        else:
            player.add_spell(Fire)
            return "I studied the pile and learned the secrets of fire magic!"

    def set_sign(self, sign):
        self.game.current_floor.layout[self.start_pos[0]][self.start_pos[1]] = sign

class Skeleton(WSPRITE):
    def __init__(self, game, x, y, gx, gy):
        super().__init__(game, x, y, gx, gy, game.enemies, color=WHITE)
        self.start_pos = (gx, gy)
        self.name = "Skeleton"
        self.sign = SKELETON + SPAWNED
        self.unspawned_sign = SKELETON
        self.set_sign(self.sign)
        self.health = 6
        self.inspect_message = f"An animated skeleton. A good fireball should do the trick."
        self.blocking = True
        self.visible = True

        # exp
        self.skip = False  # skip a tick after hitting the player
    
    def get_next_space(self):
        # Find direction vector (dx, dy) between enemy and player.
        dx, dy = self.game.player.x - self.x, self.game.player.y - self.y
        dist = math.hypot(dx, dy)
        if dist == 0:
            # dont need to move if already munching on player
            return 0, 0
        dx, dy = dx / dist, dy / dist  # Normalize.
        # Move along this normalized vector towards the player at current speed.

        # normalize and adjust for player movement
        cx = round(dx)
        cy = round(dy)

        return cx, cy
    
    def check_player_los(self):
        x = self.x
        y = self.y
        
        while x in range(0, GRIDWIDTH) and y in range(0, GRIDHEIGHT):
            dx, dy = self.get_next_space()
            x += dx
            y += dy
            try:
                for sprite in self.game.all_sprites:
                    if sprite.x == x and sprite.y == y and sprite != self:
                        if sprite.name == "Player":
                            print("see player!")
                            return True
            except Exception as e:
                print(e)
                continue
        return False
    
    def adjacent_to_player(self, newx, newy):
        px = self.game.player.x
        py = self.game.player.y

        return newx == px and newy == py

    def update(self):
        if self.visible:
            # check if we have los on the player and move if we do
            see_player = False
            if self.check_player_los():
                see_player = True
            cx, cy = self.get_next_space()
            newx = self.x + cx 
            newy = self.y + cy
            # check collisions
            blocked = False
            hit_sprite = None
            for sprite in self.game.all_sprites:
                try:
                    if sprite.x == newx and sprite.y == newy and sprite != self:
                        self.hit(sprite)
                        if sprite.blocking:
                            # if it collides with a sprite and it isnt itself, block
                            blocked = True
                except:
                    pass

            # if we are unblocked and can see the player
            # then we check if we are already next to the player
            # and if not, we move
            if not blocked and see_player and not self.skip:
                if self.adjacent_to_player(newx, newy):
                    print("on player")
                else:
                    self.gx += cx
                    self.gy += cy
                    x, y = self.game.current_floor.get_local_pos(self.gx, self.gy)
                    self.x = x
                    self.y = y
            else:
                # just adjust for viewpoint movement
                self.x -= self.game.player.dx
                self.y -= self.game.player.dy
                self.skip = False
            print(f"new skele pos: {self.x},{self.y}")
            self.rect.x = self.x * TILESIZE
            self.rect.y = self.y * TILESIZE


    def draw(self, screen):
        if self.visible:
            screen.blit(self.rect, (self.rect.x, self.rect.y))

    def set_sign(self, sign):
        self.game.current_floor.layout[self.start_pos[0]][self.start_pos[1]] = sign
    
    def take_damage(self, amount):
        self.health = self.health - amount
        self.game.log.info(f"I hit the skeleton for {amount} damage! ({self.health} hp)")
        if self.health <= 0:
            self.game.log.info("...and it killed it!")
            self.set_sign(SKELETON + DEAD)
    
    def hit(self, target):
        # can only hurt the player
        if target.name == "Player":
            print("HIT PLAYER")
            self.skip = True
            dmg = random.randint(SKDAMAGE_RANGE[0], SKDAMAGE_RANGE[1])
            print(f"skele hit for {dmg} damage")
            target.take_damage(dmg)
            
    
    def interact(self, player):
        return "I only know to kill things with magic..."
    