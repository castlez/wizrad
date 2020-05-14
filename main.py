"""
Wizrad Main Code
template from KidsCanCode
https://www.youtube.com/watch?v=3UxnelT9aCo
massively changed for my nefarious purposes
"""
import pygame as pg
from pygame.locals import *
import sys
import math
from settings import *
from sprites import *
from Floor import *
from dg.dungeonGenerationAlgorithms import RoomAddition


class Game:
    def __init__(self):
        pg.init()

        self.screen = pg.display.set_mode((WIDTH, HEIGHT), flags=DOUBLEBUF)
        self.screen.set_alpha(None)

        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        pg.key.set_repeat(500, 100)
        self.current_floor = None
        self.view = None
        self.load_data()
        self.show_grid = True

        pg.event.set_allowed([QUIT, KEYDOWN, KEYUP])

    def load_data(self):
        pass

    def new(self):
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.player = Player(self, 8, 8)

        # first floor (TODO start screen)
        self.current_floor = Floor(self, 1)
        gx, gy = self.current_floor.get_play_start()
        self.player.update_global_position(gx, gy)
        self.save_map()

    def run(self):
        # game loop - set self.playing = False to end the game
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()
    
    def save_map(self):
        map_string = ""
        fl = self.current_floor.layout
        px = self.player.global_x
        py = self.player.global_y
        print(f"Player should be at ln {py} col {px}")
        for y in range(0, MAP_HEIGHT):
            for x in range(0, MAP_WIDTH):
                if x == px and y == py:
                    map_string += "@"
                elif fl[x][y] == 9:
                    map_string += "^"
                elif fl[x][y] == 0:
                    map_string += "."
                else:
                    map_string += str(fl[x][y])
            map_string += '\n'
        with open("last_map.txt", 'w') as f:
            f.write(map_string)
        print("level map saved!")

    def quit(self, save_map=False):
        if save_map:
            self.save_map()
        
        pg.quit()
        sys.exit()

    def update(self):
        if not self.player.still:
            # use the global position of the player to decide what to draw
            cur_g_x = self.player.global_x
            cur_g_y = self.player.global_y

            # need to massage the indexes so that (xmin, ymin) is (0, 0) on the view
            xmin = cur_g_x - 6
            xmax = cur_g_x + 10
            ymin = cur_g_y - 6
            ymax = cur_g_y + 10 

            # draw the walls, i wanna explore
            fl = self.current_floor.layout
            local_x_range = range(0, GRIDWIDTH)
            local_y_range = range(0, GRIDHEIGHT)
            global_x_range = range(xmin, xmax)
            global_y_range = range(ymin, ymax)

            for ly, gy in zip(local_y_range, global_y_range):
                for lx, gx in zip(local_x_range, global_x_range):
                    if gx >= MAP_WIDTH or gy >= MAP_HEIGHT:
                        continue
                    if fl[gx][gy] == 1:
                        self.current_floor.add_wall(Wall(self, lx, ly, gx, gy))
                    elif fl[gx][gy] == 0:
                        self.current_floor.clear_space(lx, ly)

            print(f"cur floor num walls = {len(self.current_floor.walls)}")
        self.player.still = True
        self.all_sprites.update()

    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (0, y), (WIDTH, y))

    def draw(self):
        self.screen.fill(BGCOLOR)
        if self.show_grid:
            self.draw_grid()
        self.all_sprites.draw(self.screen)
        pg.display.flip()

    def events(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
                if event.key == pg.K_m:
                    self.quit(save_map=True)
                if event.key == pg.K_a:
                    self.player.move(dx=-1)
                if event.key == pg.K_d:
                    self.player.move(dx=1)
                if event.key == pg.K_w:
                    self.player.move(dy=-1)
                if event.key == pg.K_s:
                    self.player.move(dy=1)
                if event.key == pg.K_g:
                    self.show_grid = not self.show_grid
                if event.key == pg.K_l:
                    self.player.collisions = not self.player.collisions
                if event.key == pg.K_o:
                    print(f"group num walls = {len(self.walls)}")

    def show_start_screen(self):
        pass

    def show_go_screen(self):
        pass

# create the game object
g = Game()
g.show_start_screen()
while True:
    g.new()
    g.run()
    g.show_go_screen()