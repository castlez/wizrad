import pygame as pg
from spells import *
from settings import *
import traceback
import math

# Super class
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
        self.start_pos = (gx, gy)
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE
        self.inspect_message = "I have no idea what that is..."
        self.interact_message = "Not sure what I could do with that..."

        # for other sprites to check
        self.visible = True
        self.blocking = False
        self.is_enemy = False
        self.is_door = False
    
    def inspect(self):
        return self.inspect_message
    
    def interact(self, player):
        return self.interact_message
    
    def kill(self):
        super().kill()
    
    def drawt(self, screen):
        if self.visible:
            screen.blit(self.image, (self.rect.x, self.rect.y))
    
    def update(self):
        if self.visible:
            try:
                x, y = self.get_local_pos() 
                if x == -1 and y == -1:
                    return
                self.x = x - self.game.player.dx
                self.y = y - self.game.player.dy
            except Exception as e:
                print(e)
                traceback.print_exc(e)
            self.rect.x = self.x * TILESIZE
            self.rect.y = self.y * TILESIZE

    def get_local_pos(self):
        return self.game.floor.get_local_pos(self.gx, self.gy)
    
    def set_sign(self, sign):
        self.game.floor.layout[self.start_pos[0]][self.start_pos[1]] = sign
    
    def get_next_space(self, target):
        """
        TODO make this actually return a space 
        AND NOT A FUCKING DX, DY, or change the name
        """
        # Find direction vector (dx, dy) between enemy and player.
        gx = target[0]
        gy = target[1]
        dx, dy = gx - self.gx, gy - self.gy
        dist = math.hypot(dx, dy)
        if dist == 0:
            # dont need to move if already munching on player
            return 0, 0
        dx, dy = dx / dist, dy / dist  # Normalize.
        # Move along this normalized vector towards the player at current speed.

        # normalize and adjust for player movement
        cx = round(dx)
        cy = round(dy)

        # check if already diagonal to player and just
        # need to move to hit range (adjacent NON diagonal)
        if self.adjacent_to_player(self.gx, self.gy):
            if abs(cx) == 1 and abs(cy) == 1:
                # we are diagonal
                t = cx + cy
                if t == 0:
                    return 0, cy
                else:
                    return cx, 0
        return cx, cy
    
    def check_player_los(self, player):
        target = [player.gx, player.gy]
        gx = self.gx
        gy = self.gy
        spot = None
        while gx in range(0, MAP_WIDTH) and gy in range(0, MAP_HEIGHT):
            # if self.adjacent_to_player(x, y):
            #     return True
            dx, dy = self.get_next_space(target=target)
            gx += dx
            gy += dy
            for sprite in self.game.all_sprites:
                if sprite.name != "LogWindow":
                    if sprite.gx == gx and sprite.gy == gy and sprite != self:
                        if sprite.name == "Player":
                            spot = [sprite.gx, sprite.gy]
                        elif sprite.blocking:
                            return None
            if spot:
                break
        print(f"los at {spot}")
        return spot
    
    def adjacent_to_player(self, newx, newy):
        px = self.game.player.gx
        py = self.game.player.gy
        dx = abs(px - newx)
        dy = abs(py - newy)
        adjacent = dx <= 1 and dy <= 1
        return adjacent

# Walls
class Wall(WSPRITE):
    def __init__(self, game, x, y, gx, gy):
        super().__init__(game, x, y, gx, gy, game.walls, color=LIGHTGREY)
        self.inspect_message = "I think its.. well, it might be.. yeah that is! Its a wall!"
        self.blocking = True
        self.name = "Wall"
    
    def inspect(self):
        return "I think its.. well, it might be.. yeah that is! Its a wall!"
    
    def take_damage(self, amount):
        pass

class Door(WSPRITE):
    def __init__(self, element, game, x, y, gx, gy):
        # element is the element that UNLOCKS it
        # super().__init__(game, x, y, gx, gy, game.doors, color=self.get_color(element))
        super().__init__(game, x, y, gx, gy, game.doors, color=PINK)
        self.inspect_message = self.get_desc(element)
        self.element = element
        self.blocking = True
        self.is_door = True
        self.locked = True
        self.name = "Door"

    def get_desc(self, element):
        if element == FIRE:
            return "A frozen door, needs to be heated up"
        elif element == ACID:
            return "A steel door, needs to be disolved"
        elif element == ICE:
            return "A burning door, needs to cool off"
        elif element == ELEC:
            return "A digital door, needs a jolt to turn it on"
    
    def get_color(self, element):
        # if element == FIRE:
        #     return BLUE
        # elif element == ACID:
        #     return LIGHTGREY
        # elif element == ICE:
        #     return RED
        # elif element == ELEC:
        #     return YELLOW
        return PINK
    
    def inspect(self):
        return self.inspect_message

    def interact(self, player):
        if player.has_element(self.element):
            self.set_sign(self.element + DEAD)
            # TODO: make this personalized for each element
            self.game.floor.remove_inter(self)
            return "The magic leaps from my hands, unlocking the door!"
        else:
            return "Hmmm, touching the door did nothing. Perhaps I need another element?"
    
    def take_damage(self, amount):
        self.game.log.info("The spell fizzles on the door."\
                           "Perhaps touching the door once i have the right spell will work...")

# Interactables
class BurningPile(WSPRITE):
    """
    These give you fire
    """
    def __init__(self, game, x, y, gx, gy):
        super().__init__(game, x, y, gx, gy, game.inters, color=FCOLOR)
        self.inspect_message = "A magic fire, i better watch out. Hmm.. "\
                               "its interesting (right click to study)"
        self.name = "BurningPile"
        self.set_sign(FIRE + SPAWNED)
    
    def interact(self, player):
        if player.has_element(FIRE):
            return "I already know how to wield fire magic"
        else:
            fire_ball = KnownSpell(name="Fire Ball", 
                                   elements=[FIRE],
                                   description="Shoots a fireball at the cursor")
            result = player.add_spell(fire_ball)
            if result:
                return "I studied the pile and learned the secrets of fire magic!"
            else:
                return "...thus I will have to wait to wield this power..."

class IceBlock(WSPRITE):
    """
    These give you Ice
    """
    def __init__(self, game, x, y, gx, gy):
        super().__init__(game, x, y, gx, gy, game.inters, color=ICOLOR)
        self.inspect_message = "An unwavering block of ice. Hmm.. "\
                               "its interesting (right click to study)"
        self.name = "IceBlock"
        self.set_sign(ICE + SPAWNED)
    
    def interact(self, player):
        if player.has_element(ICE):
            return "I already know how to wield ice magic"
        else:
            icecycle = KnownSpell(name="Icicle",
                                   elements=[ICE],
                                   description="Shoots an icicle at the cursor")
            result = player.add_spell(icecycle)
            if result:
                return "I studied the block and learned the secrets of ice magic!"
            else:
                return "...thus I will have to wait to wield this power..."

class AcidPuddle(WSPRITE):
    """
    These give you acid
    """

    def __init__(self, game, x, y, gx, gy):
        super().__init__(game, x, y, gx, gy, game.inters, color=ACOLOR)
        self.inspect_message = "A puddle of bubbling acid. Hmm.. " \
                               "its interesting (right click to study)"
        self.name = "AcidPuddle"
        self.set_sign(ACID + SPAWNED)

    def interact(self, player):
        if player.has_element(ACID):
            return "I already know how to wield acid magic"
        else:
            acid_splash = KnownSpell(name="Acid Splash",
                                   elements=[ACID],
                                   description="Shoots an acid at the cursor")
            result = player.add_spell(acid_splash)
            if result:
                return "I studied the puddle and learned the secrets of acid magic!"
            else:
                return "...thus I will have to wait to wield this power..."

class ArcingArtifact(WSPRITE):
    """
    These give you acid
    """

    def __init__(self, game, x, y, gx, gy):
        super().__init__(game, x, y, gx, gy, game.inters, color=ECOLOR)
        self.inspect_message = "An electrified artifact. Hmm.. " \
                               "its interesting (right click to study)"
        self.name = "ArcingArtifact"
        self.set_sign(ELEC + SPAWNED)

    def interact(self, player):
        if player.has_element(ELEC):
            return "I already know how to wield electric magic"
        else:
            sparks = KnownSpell(name="sparks",
                                   elements=[ELEC],
                                   description="Shoots electric sparks at the cursor")
            result = player.add_spell(sparks)
            if result:
                return "I studied the artifact and learned the secrets of electric magic!"
            else:
                return "...thus I will have to wait to wield this power..."


class Chest(WSPRITE):
    """
    These have items in them!
    """
    def __init__(self, game, x, y, gx, gy):
        super().__init__(game, x, y, gx, gy, game.inters, color=BROWN)
        self.inspect_message = "Its a chest. Might have some loot in it..."
        self.name = "Chest"
        self.set_sign(CHEST + SPAWNED)
        self.contents = self.game.floor.get_loot()
    
    def interact(self, player):
        if self.adjacent_to_player(self.gx, self.gy):
            # if the players inven is not full, grab the item
            # and remove the chest
            got = self.game.player.get_item(self.contents)
            if got:
                self.game.floor.remove_inter(self)
                return f"Got a {self.contents.name}!"
            else:
                return "I can't carry any more :("

        else:
            return "The chest is to far away for me to open..."

class OmniGem(WSPRITE):
    def __init__(self, game, x, y, gx, gy):
        super().__init__(game, x, y, gx, gy, game.walls, color=LIGHTGREY)
        self.inspect_message = "The all mighty Omni Gem! I must harness all the elements to unlock its power!"
        self.blocking = True
        self.name = "OmniGem"
        self.colors = [FCOLOR, ICOLOR, ACOLOR, ECOLOR]
        self.set_sign(CRYSTAL + SPAWNED)

    def take_damage(self, amount):
        self.game.log.info("My spells clash against the OmniGem with no affect... Perhaps if I touched it...")

    def interact(self, player):
        """
        The win condition of the game
        """
        if player.has_element(FIRE) and player.has_element(ICE) and \
                player.has_element(ACID) and player.has_element(ELEC):
            self.game.win = True
            return "After all I've been through, the OmniGem is finally mine!"
        else:
            return "Touching the OmniGem did nothing. Maybe I need more elements?"

    def drawt(self, screen):
        if self.visible:
            cur_size = TEXT_SIZE
            x = self.rect.x
            y = self.rect.y
            for c in self.colors:
                image = pg.Surface((cur_size, cur_size))
                image.fill(c)
                #rect = image.get_rect()
                screen.blit(image, (x, y))
                cur_size -= int(cur_size*0.25)
                y += int(TILESIZE*0.25)
                x += int(TILESIZE*0.25)

# Enemies
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
        self.is_enemy = True
        self.alive = True
        self.player_last = None

        # movement
        self.skip = False  # skip a tick after hitting the player

    def update(self):
        if self.visible and self.alive:
            # check if we have los on the player and move if we do
            moved = False
            player_last = self.check_player_los(self.game.player)
            if player_last:
                if player_last != self.player_last:
                    self.player_last = player_last

            if self.player_last:
                if self.player_last[0] == self.gx and self.player_last[1] == self.gy:
                    self.player_last = None
                else:
                    cx, cy = self.get_next_space(target=self.player_last)
                    newx = self.gx + cx
                    newy = self.gy + cy
                    # check collisions
                    blocked = False
                    hit_sprite = None
                    for sprite in self.game.all_sprites:
                        try:
                            if sprite.gx == newx and sprite.gy == newy and sprite != self:
                                self.hit(sprite)
                                if sprite.blocking:
                                    # if it collides with a sprite and it isnt itself, block
                                    blocked = True
                        except:
                            pass

                    # if we are unblocked and can see the player
                    # then we check if we are already next to the player
                    # and if not, we move
                    if not blocked and not self.skip:
                        self.gx += cx - self.game.player.dx
                        self.gy += cy -self.game.player.dy

                        x, y = self.game.floor.get_local_pos(self.gx, self.gy)
                        self.x = x
                        self.y = y
                        moved = True
            if not moved:
                # just adjust for viewpoint movement
                self.x -= self.game.player.dx
                self.y -= self.game.player.dy
                self.skip = False
            self.rect.x = self.x * TILESIZE
            self.rect.y = self.y * TILESIZE

    def draw(self, screen):
        print("drawing skele")
        if self.visible and self.alive:
            screen.blit(self.rect, (self.rect.x, self.rect.y))
    
    def take_damage(self, amount):
        if self.alive:
            self.health = self.health - amount
            self.game.log.info(f"I hit the skeleton for {amount} damage! ({self.health} hp)")
            if self.health <= 0:
                self.game.log.info("...and it killed it!")
                self.game.player.gain_xp(SK_XP)
                self.set_sign(SKELETON + DEAD)
                self.game.floor.remove_enemy(self)
                self.alive = False
    
    def hit(self, target):
        # can only hurt the player
        if target.name == "Player":
            self.skip = True
            dmg = random.randint(SKDAMAGE_RANGE[0], SKDAMAGE_RANGE[1]+1)
            target.take_damage(self, dmg)
            
    
    def interact(self, player):
        return "I only know to kill things with magic... (Press space to fire at cursor)"
    