"""
Floor stuff
"""
from settings import *
from sprites import *
import os
import json
import random

from dg.dungeonGenerationAlgorithms import RoomAddition

class Floor:
    """
    Handles the floor and all its rooms
    for self.layout:
        0 is empty floor
        1 is wall
        2 is enemy
        ...
    """

    def __init__(self, game, floor_number):
        self.fire = []
        self.ice = []
        self.secret = []
        self.enemies = []
        self.inters = []
        self.floor_number = floor_number
        self.walls = []
        # current view port, [[xmin, xmax], [ymin, ymax]]
        self.current_view = [[0, 0],[0, 0]]
        self.game = game

        generator = RoomAddition()
        self.layout = generator.generateLevel(MAP_WIDTH, MAP_HEIGHT)
        print("Level Loaded!")
    
    def get_valid_pos(self):
        while True:
            x = random.randint(1, MAP_WIDTH-1)
            y = random.randint(1, MAP_HEIGHT-1)
            if self.layout[x][y] == 0:
                return x, y
    
    def clear_space(self, x, y):
        # TODO: i dont want to have to do this
        # for every type of thing in a floor
        # ACTUALLY i shouldnt be drawing new stuff
        # this often, i shouldnt need this function...
        for wall in self.walls:
            if wall.x == x and wall.y == y:
                wall.kill()
        for inter in self.inters:
            if inter.x == x and inter.y == y:
                inter.kill()

    def add_wall(self, wall):
        self.walls.append(wall)
    
    def add_inter(self, interactable):
        self.inters.append(interactable)
    
    def add_enemy(self, enemy):
        self.enemies.append(enemy)
    
    def remove_enemy(self, enemy):
        print("removing enemy")
        self.enemies[enemy].kill()
        del self.enemies[enemy]

    def get_local_pos(self, gx, gy):
        xmin = self.current_view[0][0]
        xmax = self.current_view[0][1]
        ymin = self.current_view[1][0]
        ymax = self.current_view[1][1]

        if gx < xmin or gx > xmax or gy < ymin or gy > ymax:
            return None
        
        lx = gx - xmin
        ly = gy - ymin
        return lx, ly
    
    def purge_unseen(self):
        xmin = self.current_view[0][0]
        xmax = self.current_view[0][1]
        ymin = self.current_view[1][0]
        ymax = self.current_view[1][1]
        
        # walls
        for i, wall in enumerate(self.walls):
            if wall.x < xmin or wall.x > xmax or wall.y < ymin or wall.y > ymax:
                wall.kill()
                del self.walls[i]
        
        # interactable objects
        for i, inter in enumerate(self.inters):
            if inter.gx < xmin or inter.gx > xmax or inter.gy < ymin or inter.gy > ymax:
                inter.visible = False
        
        # enemies TODO improve this system
        for i, enemy in enumerate(self.enemies):
            if enemy.health < 0:
                self.remove_enemy(i)
            elif enemy.gx < xmin or enemy.gx > xmax or enemy.gy < ymin or enemy.gy > ymax:
                enemy.visible = False
    
    def update_seen(self):
        """
        if something is still in the lists
        set its visible to true
        """
        xmin = self.current_view[0][0]
        xmax = self.current_view[0][1]
        ymin = self.current_view[1][0]
        ymax = self.current_view[1][1]

        # walls
        for wall in self.walls:
            wall.visible = True
        
        # interactable objects
        for inter in self.inters:
            inter.visible = True
                
        # enemies TODO improve this system
        for enemy in self.enemies:
            enemy.visible = True


    def update_viewport(self, gx, gy):
        # need to massage the indexes so that (xmin, ymin) is (0, 0) on the view
        xmin = gx - 6
        xmax = gx + 10
        ymin = gy - 6
        ymax = gy + 10 

        # update the current view and purge anything
        # no longer visible
        self.current_view = [[xmin, xmax], [ymin, ymax]]
        self.purge_unseen()
        self.update_seen()

        # get ranges for viewport and the corresponding area
        # in the global map
        fl = self.layout
        local_x_range = range(0, GRIDWIDTH)
        local_y_range = range(0, GRIDHEIGHT)
        global_x_range = range(xmin, xmax)
        global_y_range = range(ymin, ymax)

        # add the new walls, inters, enemies, etc, and keep the floor clear
        for ly, gy in zip(local_y_range, global_y_range):
            for lx, gx in zip(local_x_range, global_x_range):
                if gx >= MAP_WIDTH or gy >= MAP_HEIGHT:
                    continue
                try:
                    value = fl[gx][gy]
                except:
                    return
                if value == 1:
                    self.add_wall(Wall(self.game, lx, ly, gx, gy))
                elif value == FIRE:
                    self.add_inter(BurningPile(self.game, lx, ly, gx, gy))
                elif value == SKELETON:
                    sk = Skeleton(self.game, lx, ly, gx, gy)
                    self.add_enemy(sk)
                else:
                    try:
                        sprite_at = self.game.get_sprite_at(lx, ly)
                        if sprite_at and sprite_at.name == "Wall":
                            self.clear_space(lx, ly)
                    except Exception as e:
                        print(e)

    def populate_floor(self):
        """
        Populates the map with stuff
        """
        
        # fire
        num_fire = random.randint(FMIN, FMAX)
        for _ in range(num_fire):
            x, y = self.get_valid_pos()
            self.layout[x][y] = FIRE
        
        # skeletons
        num_skele = random.randint(SKMIN, SKMAX)
        for _ in range(num_skele):
            x, y = self.get_valid_pos()
            self.layout[x][y] = SKELETON

