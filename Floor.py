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
        for wall in self.walls:
            if wall.x == x and wall.y == y:
                wall.kill()

    def add_wall(self, wall):
        self.walls.append(wall)
    
    def add_inter(self, interactable):
        self.inters.append(interactable)
    
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
            if inter.x < xmin or inter.x > xmax or inter.y < ymin or inter.y > ymax:
                inter.kill()
                del self.inters[i]
        
    
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

        # get ranges for viewport and the corresponding area
        # in the global map
        fl = self.layout
        local_x_range = range(0, GRIDWIDTH)
        local_y_range = range(0, GRIDHEIGHT)
        global_x_range = range(xmin, xmax)
        global_y_range = range(ymin, ymax)

        # add the new walls and keep the floor clear
        for ly, gy in zip(local_y_range, global_y_range):
            for lx, gx in zip(local_x_range, global_x_range):
                if gx >= MAP_WIDTH or gy >= MAP_HEIGHT:
                    continue
                
                value = fl[gx][gy]
                if value == 1:
                    self.add_wall(Wall(self.game, lx, ly, gx, gy))
                elif value == "f":
                    self.add_inter(BurningPile(self.game, lx, ly, gx, gy))
                elif fl[gx][gy] == 0:
                    self.clear_space(lx, ly)

    def populate_floor(self):
        """
        Populates the map with stuff
        """
        
        # fire
        num_fire = random.randint(FMIN, FMAX)
        for _ in range(num_fire):
            x, y = self.get_valid_pos()
            self.layout[x][y] = FIRE

