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
from LogWindow import *
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
        self.log = None

        pg.event.set_allowed([QUIT, KEYDOWN, KEYUP])

    def load_data(self):
        pass

    def new(self):
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.inters = pg.sprite.Group()
        self.player = Player(self, 8, 8)
        self.log = LogWindow(self, 3, 15)

        # first floor (TODO start screen)
        self.current_floor = Floor(self, 1)
        self.current_floor.populate_floor()

        # put the player in a random place
        gx, gy = self.current_floor.get_valid_pos()
        self.player.update_global_position(gx, gy)

        # TODO remove
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
        if not os.path.exists("scraps"):
            os.makedirs("scraps")
        with open("scraps/last_map.txt", 'w') as f:
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

            self.current_floor.update_viewport(cur_g_x, cur_g_y)
            
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
                if event.key == pg.K_DOWN:
                    self.log.update_place(change=-1)
                if event.key == pg.K_UP:
                    self.log.update_place(change=1)
            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                mouse_pos = pg.mouse.get_pos()
                message = ""
                for sprite in self.all_sprites:
                    try:
                        message = sprite.inspect(mouse_pos)
                        if message:
                            break
                    except Exception as e:
                        self.log.info(e)
                        continue
                if message != "" and message != None:
                    self.log.info(message)
                else:
                    self.log.info("Its the floor. Im looking at the floor... "
                                  "Maybe i should look at other things")
                

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