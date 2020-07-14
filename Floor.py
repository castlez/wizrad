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

 # add two tuples component wise (WHY DOESNT THIS ALREADY EXIST?!)
add_tuples = lambda t1, t2: [t1[0]+t2[0], t1[1]+t2[1]]

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
    
    def get_adjacent_walls(self, gx, gy):
        """
        returns a list of (dx, dy) tuples detailing
        the directions of any walls, empty if none
        """

        fl = self.layout
        walls = []

        # right, left, down, up
        if fl[gx+1][gy] == WALL:
            walls.append((1, 0))
        if fl[gx-1][gy] == WALL:
            walls.append((-1, 0))
        if fl[gx][gy+1] == WALL:
            walls.append((0, 1))
        if fl[gx][gy-1] == WALL:
            walls.append((0, -1))
        
        # diagonals
        if fl[gx+1][gy+1] == WALL:
            walls.append((1, 1))
        if fl[gx-1][gy+1] == WALL:
            walls.append((-1, 1))
        if fl[gx+1][gy-1] == WALL:
            walls.append((1, -1))
        if fl[gx-1][gy-1] == WALL:
            walls.append((-1, -1))
        
        return walls
        

    def find_doorways(self, start_pos):
        """
        Returns the coordinates of all doors in a given room
        """
        fl = self.layout
        with open(os.getcwd() + "\\debug.txt", 'w') as f:
            mp = ""
            for y in range(MAP_HEIGHT):
                for x in range(MAP_WIDTH):
                    w = fl[x][y] if fl[x][y] == 1 else "."
                    mp += f"{w}"
                mp += "\n"
            f.write(mp)
        doorways = []

        # bounds for traversal (perimeter of room)
        xmin = None
        xmax = None
        ymin = None
        ymax = None
        
        # track the bounds we've found around
        found_bounds = [0,0,0,0]
        
        # Find the bounds of the room (up: ymin, down: ymax, left: xmin, right:xmax)
        for direction in [[1,0], [-1,0], [0,1], [0,-1]]:
            # reset starting position for each direction
            coordx = start_pos[0]
            coordy = start_pos[1]
            found = False
            while not found:
                adjacent = self.get_adjacent_walls(coordx, coordy)
                if len(adjacent) > 0:
                    for adj in adjacent:
                        if adj[0] == 1:
                            xmax = coordx
                            found_bounds[0] = 1
                            found = True
                        elif adj[0] == -1:
                            xmin = coordx
                            found_bounds[1] = 1
                            found = True
                        if adj[1] == 1:
                            ymax = coordy
                            found_bounds[2] = 1
                            found = True
                        elif adj[1] == -1:
                            ymin = coordy
                            found_bounds[3] = 1
                            found = True
                print(f"total bounds found = {sum(found_bounds)}, {found_bounds}")
                print(f"cur pos = {coordx}, {coordy}")
                # move to the next space
                new_coords = add_tuples([coordx, coordy], direction)
                coordx = new_coords[0]
                coordy = new_coords[1]

            if sum(found_bounds) == 4:
                break
        
        if sum(found_bounds) == 4:
                print("FOUND ALL BOUNDS")
        else:
            print(f"FAILED to find bounds of room at {start_pos}")
            return
        
        if fl[xmin-1][ymin] == 1 and fl[xmin-1][ymin-1] == 1 and fl[xmin][ymin-1] == 1:
            print(f"({xmin}, {ymin}) is a corner!")
        
        # now that we have the bounds, use them to search for doorways
        
        # first fix y and traverse x
        for x in range(xmin, xmax+1):
            if fl[x][ymin-1] == 0:
                doorways.append([x, ymin-1])
            elif fl[x][ymax+1] == 0:
                doorways.append([x, ymax+1])
            
        # next fix x and and traverse y
        for y in range(ymin, ymax+1):
            if fl[xmin-1][y] == 0:
                doorways.append([xmin-1, y])
            elif fl[xmax+1][y] == 0:
                doorways.append([xmax+1, y])
        
        return doorways

    def populate_floor(self):
        """
        Populates the map with stuff
        """
        #### Doors
        doors = [FDOOR, IDOOR, ADOOR, EDOOR]
        for rxy in self.room_centers:
            if len(doors) == 0:
                # placed all the doors
                break
            doorways = self.find_doorways(rxy)
            if doorways:
                if len(doorways) >= 1:
                    dc = doorways[0]  # door coords
                    self.layout[dc[0]][dc[1]] = doors.pop()
                elif len(doorways) == 0:
                    break
                else:
                    continue

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

