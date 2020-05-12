"""
Rooms stuff
"""
from settings import *
from sprites import *
import os
import json

class Room:

    def __init__(self, game, room_name):
        self.room_name = room_name
        self.walls = []
        self.fire = []
        self.ice = []
        self.secret = []
        self.enemies = []

        room_path = os.path.join(os.getcwd(), "Rooms", room_name + ".json")
        with open(room_path, 'r') as room_file:
            room_json = json.loads(room_file.read())
        
        for ws in room_json["wall"]:
            wall_from = [ws[0], ws[1]]
            wall_to = [ws[2], ws[3]]

            # determine axis, 0 is x, 1 is y
            if wall_from[1] == wall_to[1]:
                axis = 0
            else:
                axis = 1
            if axis == 0:
                for x in range(wall_from[0], wall_to[0]):
                    self.walls.append(Wall(game, x, wall_to[1]))
            else:
                for y in range(wall_from[1], wall_to[1]):
                    self.walls.append(Wall(game, wall_to[0], y))

            


        
