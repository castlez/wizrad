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
        self.floor_number = floor_number
        self.walls = []

        generator = RoomAddition()
        self.layout = generator.generateLevel(MAP_WIDTH, MAP_HEIGHT)
        print("Level Loaded!")
    
    def get_play_start(self):
        while True:
            x = random.randint(1, MAP_WIDTH-1)
            y = random.randint(1, MAP_HEIGHT-1)
            if self.layout[x][y] == 0:
                print(f"setting player position to ln {y} col {x}")
                return x, y
    
    def clear_space(self, x, y):
        for wall in self.walls:
            if wall.x == x and wall.y == y:
                wall.kill()

    def add_wall(self, wall):
        self.walls.append(wall)
        
        


       

            


        
