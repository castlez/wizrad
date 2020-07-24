"""
Floor stuff
"""
import os
import random

from math import sqrt

from Items import HealingPotion
from dg.dungeonGenerationAlgorithms import RoomAddition
from settings import *
from settings import FIRE, ACID, ICE, ELEC

# add two tuples component wise (WHY DOESNT THIS ALREADY EXIST?!)
from sprites import Wall, BurningPile, IceBlock, Skeleton, Chest, Door, AcidPuddle, ArcingArtifact, OmniGem

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
        self.layout, self.rooms = generator.generateLevel(MAP_WIDTH, MAP_HEIGHT)

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
        """
        Get a random position that is currently ground
        :return:
        """
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
        """
        take a global coord and convert it into
        a local position on the screen
        :param gx:
        :param gy:
        :return:
        """
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
        """
        Remove dead enemies and opened doors
        :return:
        """
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
        """
        Draw a box around the player (figuratively) and
        updates the visibility and spawning of stuff
        :param gx:
        :param gy:
        :return:
        """
        # need to massage the indexes so that (xmin, ymin) is (0, 0) on the view
        xmin = gx - PLAYER_X
        xmax = gx + PLAYER_X + 2
        ymin = gy - PLAYER_Y
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
                if gx not in range(0, MAP_WIDTH) or gy not in range(0, MAP_HEIGHT):
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
                elif value == ACID:
                    self.add_inter(AcidPuddle(self.game, lx, ly, gx, gy))
                elif value == ELEC:
                    self.add_inter(ArcingArtifact(self.game, lx, ly, gx, gy))
                elif value == SKELETON:
                    sk = Skeleton(self.game, lx, ly, gx, gy)
                    self.add_enemy(sk)
                elif value == CHEST:
                    self.add_inter(Chest(self.game, lx, ly, gx, gy))
                elif value in [FDOOR, IDOOR, EDOOR, ADOOR]:
                    self.add_door(Door(DEM[value], self.game, lx, ly, gx, gy))
                elif value == CRYSTAL:
                    self.add_inter(OmniGem(self.game, lx, ly, gx, gy))
                else:
                    pass
        
    def get_room_center(self, room):
        """
        Gets the point closest to the center of the room
        Only need three corners
        :param room:
        :return:
        """
        corners = room["corners"]
        tl = corners[0]
        tr = corners[1]
        bl = corners[2]

        len_x = tr[0] - tl[0]
        len_y = bl[1] - tl[1]

        mid_x = tr[0] - int(len_x/2)
        mid_y = bl[1] - int(len_y/2)

        return [mid_x, mid_y]

    def get_room(self, x, y):
        for r in self.rooms:
            tl = r["corners"][0]
            tr = r["corners"][1]
            bl = r["corners"][2]
            br = r["corners"][3]
            if x >= tl[0] and x <= tr[0]:
                if y >= tl[1] and y <= bl[1]:
                    return r

        return None
    
    def find_doors(self, room):
        """
        HACK figure it out the dumb dumb way
        :param room: 
        :return: 
        """
        tl = room["corners"][0]
        tr = room["corners"][1]
        bl = room["corners"][2]
        br = room["corners"][3]
        doors = []
        # can get away with check if its not a wall because
        # only walls and doors have been rendered so far
        for x in range(tl[0], tr[0]+1):
            if self.layout[x][tl[1]-1] != 1:
                doors.append([x, tl[1]-1])
            if self.layout[x][bl[1]+1] != 1:
                doors.append([x, bl[1]+1])
        for y in range(tl[1], bl[1]+1):
            if self.layout[tl[0]-1][y] != 1:
                doors.append([tl[0]-1, y])
            if self.layout[tr[0]+1][y] != 1:
                doors.append([tr[0]+1, y])
        return doors

    def validate_floor(self):
        """
        Checks that all 5 of the expected doors have
        been placed
        :return: bool
        """
        needed_doors = [FDOOR, IDOOR, ADOOR, EDOOR, FDOOR]
        fl = self.layout
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                if fl[x][y] in needed_doors:
                    needed_doors.remove(fl[x][y])
        return len(needed_doors) == 0

    def populate_floor(self):
        """
        Populates the map with stuff
        """
        #### Doors
        door_types = [FDOOR, IDOOR, ADOOR, EDOOR, FDOOR]
        room_val = 0
        placed = False
        ppos = None
        while len(door_types) != 0:
            rand_room = random.randint(0, len(self.rooms)-1)
            room = self.rooms[rand_room]
            doors = self.find_doors(room)
            if len(doors) == 1:
                dtype = door_types.pop()
                etype = DEM[dtype]
                door = doors[0]
                if self.layout[door[0]][door[1]] == 0:
                    print(f"placing {etype} at {door}")
                    center = self.get_room_center(room)
                    ex = center[0]
                    ey = center[1]
                    if etype == FIRE:
                        if not ppos:
                            self.layout[ex][ey] = FIRE
                            self.layout[ex-1][ey] = PLAYER
                            ppos = [ex-1, ey]
                        else:
                            self.layout[ex][ey] = ICE
                    if etype == ICE:
                        self.layout[ex][ey] = ACID
                    if etype == ACID:
                        self.layout[ex][ey] = ELEC
                    if etype == ELEC:
                        self.layout[ex][ey] = CRYSTAL

                    self.layout[door[0]][door[1]] = dtype
                    print(f"door at {door}")
        if DEBUG:
            print(f"player at : {ppos}")
            print("done with doors and elements")
            fl = self.layout
            with open(os.getcwd() + "\\scraps\\debug.txt", 'w') as f:
                mp = ""
                for y in range(MAP_HEIGHT):
                    for x in range(MAP_WIDTH):
                        w = "." if fl[x][y] == 0 else fl[x][y]
                        mp += f"{w}"
                    mp += "\n"
                f.write(mp)

        # skeletons
        # dont spawn em to close
        # d=√((x_2-x_1)²+(y_2-y_1)²)
        num_skele = random.randint(SKMIN, SKMAX)
        px = ppos[0]
        py = ppos[1]
        for _ in range(num_skele):
            placed = False
            tries = 3
            while not placed and tries > 0:
                x, y = self.get_valid_pos()
                d = int(sqrt(abs((x - px)**2 - (y - py)**2)))
                if d > S_START_RADIUS:
                    if self.layout[x][y] == 0:
                        self.layout[x][y] = SKELETON
                        placed = True
                else:
                    tries -= 1
        
        # chests
        num_chest = random.randint(CHMIN, CHMAX)
        for _ in range(num_chest):
            x, y = self.get_valid_pos()
            self.layout[x][y] = CHEST

