"""
Floor stuff
"""
from settings import *
from sprites import *
from Items import *
import os
import json
import random
import traceback

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
        self.doors = []
        self.floor_number = floor_number
        self.walls = []
        self.wall_locs = []

        self.all = []
        # current view port, [[xmin, xmax], [ymin, ymax]]
        self.current_view = [[0, 0],[0, 0]]
        self.game = game

        # layout
        generator = RoomAddition()
        self.layout, self.room_centers = generator.generateLevel(MAP_WIDTH, MAP_HEIGHT)

        # loot
        self.loot_table = None
        self.set_loot_table()
        print("Level Loaded!")
    
    def set_loot_table(self):
        """
        Sets the loot table based on floor
        """
        if self.floor_number == 1:
            self.loot_table = [HealingPotion]

    def get_loot(self):
        """
        Gets a random item from the loot table
        """
        item_index = random.randint(0, len(self.loot_table)-1)
        item = self.loot_table[item_index](self.game)
        return item
    
    def get_valid_pos(self):
        while True:
            x = random.randint(1, MAP_WIDTH-1)
            y = random.randint(1, MAP_HEIGHT-1)
            if self.layout[x][y] == 0:
                return x, y

    def add_wall(self, wall):
        self.walls.append(wall)
        self.all.append(wall)
        self.wall_locs.append((wall.gx, wall.gy))
    
    def add_inter(self, interactable):
        self.inters.append(interactable)
        self.all.append(interactable)
    
    def remove_inter(self, interactable):
        interactable.kill()
        self.inters.remove(interactable)
        self.all.remove(interactable)
    
    def add_enemy(self, enemy):
        self.enemies.append(enemy)
        self.all.append(enemy)
    
    def add_door(self, door):
        self.doors.append(door)
        self.all.append(door)
    
    def remove_door(self, door):
        door.kill()
        self.doors.remove(door)
        self.all.remove(door)
    
    def remove_enemy(self, enemy):
        enemy.kill()
        self.enemies.remove(enemy)
        self.all.remove(enemy)

    def get_local_pos(self, gx, gy):
        xmin = self.current_view[0][0]
        xmax = self.current_view[0][1]
        ymin = self.current_view[1][0]
        ymax = self.current_view[1][1]

        if gx < xmin or gx > xmax or gy < ymin or gy > ymax:
            return -1, -1
        
        lx = gx - xmin
        ly = gy - ymin
        return lx, ly
    
    def purge_unseen(self):
        xmin = self.current_view[0][0]
        xmax = self.current_view[0][1]
        ymin = self.current_view[1][0]
        ymax = self.current_view[1][1]

        for sprite in self.all:
            if sprite.x < xmin or sprite.x > xmax or sprite.y < ymin or sprite.y > ymax:
                sprite.visible = False
            if sprite.is_enemy:
                if sprite.health < 0:
                    self.remove_enemy(sprite)
            if sprite.is_door:
                pos = [sprite.gx, sprite.gy]
                if self.layout[pos[0]][pos[1]] == sprite.element + DEAD:
                    print("REMOVING DOOR")
                    self.remove_door(sprite)
    
    def update_seen(self):
        """
        if something is still in the lists
        set its visible to true
        """
        xmin = self.current_view[0][0]
        xmax = self.current_view[0][1]
        ymin = self.current_view[1][0]
        ymax = self.current_view[1][1]

        for sprite in self.all:
            sprite.visible = True

    def update_viewport(self, gx, gy):
        # need to massage the indexes so that (xmin, ymin) is (0, 0) on the view
        xmin = gx - PLAYER_X - 2
        xmax = gx + PLAYER_X + 2
        ymin = gy - PLAYER_Y - 2
        ymax = gy + PLAYER_Y + 2

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
                    if not (gx, gy) in self.wall_locs:
                        self.add_wall(Wall(self.game, lx, ly, gx, gy))
                elif value == FIRE:
                    self.add_inter(BurningPile(self.game, lx, ly, gx, gy))
                elif value == ICE:
                    self.add_inter(IceBlock(self.game, lx, ly, gx, gy))
                elif value == SKELETON:
                    sk = Skeleton(self.game, lx, ly, gx, gy)
                    self.add_enemy(sk)
                elif value == CHEST:
                    self.add_inter(Chest(self.game, lx, ly, gx, gy))
                elif value in [FDOOR, IDOOR, EDOOR, ADOOR]:
                    self.add_door(Door(DEM[value], self.game, lx, ly, gx, gy))
                else:
                    pass
    
    def find_doors(self, start_pos):
        """
        Returns the coordinates of all doors in a given room
        """
        cur = start_pos
        fl = self.layout
        opennings = []
        
        # first find the wall to the left
        wall_hit = False
        while not wall_hit:
            check = [cur[0]-1, cur[1]]
            if fl[check[0]][check[1]] == 1:
                wall_hit = True
            else:
                cur = [cur[0]-1, cur[1]]
        xmin = cur[0]

        # now follow the wall collecting all opennings in a list
        start = cur
        done = False
        while not done:
            break

        # TODO: since rooms are rectangles, find the xmax,xmin and ymax ymin and traverse
        # TODO: to find Openings

        return start_pos

    def populate_floor(self):
        """
        Populates the map with stuff
        """
        #### Doors
        doors = [FDOOR, IDOOR, ADOOR, EDOOR]
        for rxy in self.room_centers:
            doorways = self.find_doors(rxy)
            if len(doorways) != 1:
                continue
            elif len(doors) == 0:
                break
            else:
                dc = doorways[0]  # door coords
                if self.layout[dc[0]][dc[1]] == 0:  # temp till i get door locs right
                    self.layout[dc[0]][dc[1]] = doors.pop()

        # fire
        num_fire = random.randint(FMIN, FMAX)
        for _ in range(num_fire):
            x, y = self.get_valid_pos()
            self.layout[x][y] = FIRE
        
        # ice
        num_ice = random.randint(FMIN, FMAX)
        for _ in range(num_ice):
            x, y = self.get_valid_pos()
            self.layout[x][y] = ICE

        # skeletons
        num_skele = random.randint(SKMIN, SKMAX)
        for _ in range(num_skele):
            x, y = self.get_valid_pos()
            self.layout[x][y] = SKELETON
        
        # chests
        num_chest = random.randint(CHMIN, CHMAX)
        for _ in range(num_chest):
            x, y = self.get_valid_pos()
            self.layout[x][y] = CHEST

