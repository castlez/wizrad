import pygame as pg
from settings import *

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
        

class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y, gx, gy):
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.gx = gx
        self.gy = gy
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE
    
    def update(self):
        # use the global position of the player to decide what to draw
        cur_g_x = self.game.player.global_x
        cur_g_y = self.game.player.global_y

        # need to massage the indexes so that (xmin, ymin) is (0, 0) on the view
        xmin = cur_g_x - 6
        xmax = cur_g_x + 10
        ymin = cur_g_y - 6
        ymax = cur_g_y + 10
        if self.gx < xmin or self.gx > xmax or self.gy < ymin or self.gy > ymax:
            self.kill()