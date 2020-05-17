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
from player import *
from dg.dungeonGenerationAlgorithms import RoomAddition


class Game:
    def __init__(self):
        pg.init()

        self.screen = pg.display.set_mode((WIDTH, HEIGHT), flags=DOUBLEBUF)
        self.screen.set_alpha(None)

        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        pg.key.set_repeat(SPRINT_DELAY, SPRINT_SPEED)
        self.current_floor = None
        self.view = None
        self.load_data()
        self.show_grid = True
        self.log = None
        self.tick = False

        pg.event.set_allowed([QUIT, KEYDOWN, KEYUP])

    def load_data(self):
        pass

    def new(self):
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.inters = pg.sprite.Group()
        self.spells = pg.sprite.Group()
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
        self.log.init()
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()
        return self.playing
    
    def save_map(self):
        map_string = ""
        fl = self.current_floor.layout
        px = self.player.global_x
        py = self.player.global_y
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
        print("level map saved in scraps/last_map.txt!")

    def quit(self, save_map=False):
        if save_map:
            self.save_map()
        
        pg.quit()
        sys.exit()

    def update(self):
        # only update on tick
        # (currently just player movement)
        if not self.player.still:
            self.tick = True
        
        if self.tick:
            # use the global position of the player to decide what to draw
            cur_g_x = self.player.global_x
            cur_g_y = self.player.global_y

            self.current_floor.update_viewport(cur_g_x, cur_g_y)
            self.all_sprites.update()
            self.spells.update()    
            self.player.still = True
            self.tick = False
            self.player.dx = 0
            self.player.dy = 0
        self.log.update()

        if not self.player.state.alive:
            self.playing = False

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
        # if self.player.is_firing:
        self.spells.draw(self.screen)
        self.log.draw(self.screen)
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
                    self.log.update_place(change=1)
                if event.key == pg.K_UP:
                    self.log.update_place(change=-1)
                if event.key == pg.K_p:
                    self.log.info(f"current spells: {self.player.get_spells()}")
                if event.key == pg.K_e:
                    self.log.info(f"current equipped spell: {self.player.equipped_spell}")
                if event.key == pg.K_SPACE:
                    if not self.player.is_firing:
                        mouse_pos = pg.mouse.get_pos()
                        self.player.fire_spell(mouse_pos)
                if event.key == pg.K_RETURN:
                    self.tick = True
            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                mouse_pos = pg.mouse.get_pos()
                self.player.inspect_space(mouse_pos)
                self.tick = True
            elif event.type == pg.MOUSEBUTTONUP and event.button == 3:
                mouse_pos = pg.mouse.get_pos()
                self.player.interact_space(mouse_pos)
    
    def object_in_view(self, gx, gy):
        """
        gx and gy are global quards
        """
        # use the global position of the player to decide what to draw
        cur_g_x = self.player.global_x
        cur_g_y = self.player.global_y

        # need to massage the indexes so that (xmin, ymin) is (0, 0) on the view
        xmin = cur_g_x - 6
        xmax = cur_g_x + 10
        ymin = cur_g_y - 6
        ymax = cur_g_y + 10

        # if we are out of sight, despawn
        if gx < xmin or gx > xmax or gy < ymin or gy > ymax:
            return False
        return True

    def show_start_screen(self):
        pass

    def show_go_screen(self):
        pass

# create the game object
while True:
    print(" ________  new game ________")
    g = Game()
    g.show_start_screen()
    alive = True
    while alive:
        g.new()
        alive = g.run()
    pg.quit()
