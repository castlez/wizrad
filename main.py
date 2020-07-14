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
from Screens import *
from controls import *
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
        self.show_inventory = False
        self.godmode = GODMODE

        pg.event.set_allowed([QUIT, KEYDOWN, KEYUP])

    def load_data(self):
        pass

    def new(self):
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.inters = pg.sprite.Group()
        self.spells = pg.sprite.Group()
        self.playerg = pg.sprite.Group()
        self.doors = pg.sprite.Group()
        self.screens = pg.sprite.Group()
        self.player = Player(self, PLAYER_X, PLAYER_Y)
        self.log = LogWindow(self, 3, 15)
        self.inventory = Inventory(self, 0, 0)

        # first floor (TODO start screen)
        self.current_floor = Floor(self, 1)
        self.current_floor.populate_floor()

        # put the player in a random place
        gx, gy = self.current_floor.get_valid_pos()
        self.player.update_global_position(gx, gy)

        # start the engines
        self.tick = True

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
        px = self.player.gx
        py = self.player.gy
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

        if self.show_inventory:
            self.inventory.update()
        elif self.tick:  # NOTE: might be able to toggle turn based here... 
            # use the global position of the player to decide what to draw
            cur_g_x = self.player.gx
            cur_g_y = self.player.gy

            self.playerg.update()
            self.walls.update()
            self.spells.update()
            self.enemies.update()
            self.inters.update()
            self.doors.update()
            self.current_floor.update_viewport(cur_g_x, cur_g_y)
            self.player.still = True
            self.tick = False
            self.player.dx = 0
            self.player.dy = 0
        self.log.update()

        if not self.player.state.alive:
            self.playing = False
        

    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, DARKGREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, DARKGREY, (0, y), (WIDTH, y))

    def draw(self):
        if self.show_inventory:
            self.inventory.drawt(self.screen)
        else:
            self.screen.fill(BGCOLOR)
            for wall in self.walls:
                wall.drawt(self.screen)
            for enemy in self.enemies:
                enemy.drawt(self.screen)
            for inter in self.inters:
                inter.drawt(self.screen)
            for spell in self.spells:
                spell.drawt(self.screen)
            for door in self.doors:
                door.drawt(self.screen)
            if self.show_grid:
                self.draw_grid()
            self.player.drawt(self.screen)
        self.log.draw(self.screen)
        pg.display.flip()

    def events(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if self.show_inventory:
                if event.type == pg.KEYDOWN:
                    if INVENTORY(event):
                        self.show_inventory = False
                elif INSPECT(event):
                    mouse_pos = pg.mouse.get_pos()
                    self.inventory.check(mouse_pos)
                elif INTERACT(event):
                    mouse_pos = pg.mouse.get_pos()
                    self.inventory.select(mouse_pos)
            else:
                if event.type == pg.KEYDOWN:
                    if QUIT_GAME(event):
                        self.quit()
                    if QUIT_SAVE(event):
                        self.quit(save_map=True)
                    if MOVE_LEFT(event):
                        self.player.move(dx=-1)
                    if MOVE_RIGHT(event):
                        self.player.move(dx=1)
                    if MOVE_UP(event):
                        self.player.move(dy=-1)
                    if MOVE_DOWN(event):
                        self.player.move(dy=1)
                    if FIRE_SPELL(event):
                        # if not self.player.is_firing: TODO maybe limit this?
                        self.tick = True
                        mouse_pos = pg.mouse.get_pos()
                        self.player.fire_spell(mouse_pos)
                    if DO_TICK(event):
                        self.tick = True
                    if USE_ITEM(event):
                        self.player.use_item()
                    if SHOW_GRID(event):
                        self.show_grid = not self.show_grid
                    if GODMODE(event): 
                        self.godmode = not self.godmode
                        self.log.info(f"GODMODE ON: {self.godmode}")
                    if INVENTORY(event):
                        self.show_inventory = True
                    if PRINT_STATS(event):
                        print("--- STATS -----")
                        print(f"player = {[self.player.gx, self.player.gy]}")
                        print(f"player(txt) = {[self.player.gy-1, self.player.gx-1]}")
                        print(f"walls = {len(self.walls)}")
                        print(f"enemies = {len(self.enemies)}")
                        print(f"doors:")
                        for d in self.doors:
                            print(f"{d.element}: {[d.gx, d.gy]}")
                        print("---------------")
                    if LOG_SCROLL_DOWN(event):
                        self.log.update_place(change=1)
                    if LOG_SCROLL_UP(event):
                        self.log.update_place(change=-1)
                    if HELP(event):
                        self.help()
                elif INSPECT(event):
                    mouse_pos = pg.mouse.get_pos()
                    self.player.inspect_space(mouse_pos)
                    self.tick = True
                elif INTERACT(event):
                    mouse_pos = pg.mouse.get_pos()
                    self.player.interact_space(mouse_pos)

    def get_sprite_at(self, x, y):
        for sprite in self.all_sprites:
            try:
                if sprite.x == x and sprite.y == y:
                    return sprite
            except:
                pass
        return None
    
    def help(self):
        """
        prints the help message
        """
        self.log.info("[H, help]  [L-Click inspect]  [R-Click, interact ]  [Space, fire spell ]  [I, inventory]")
    
    def object_in_view(self, gx, gy):
        """
        gx and gy are global quards
        """
        # use the global position of the player to decide what to draw
        cur_g_x = self.player.gx
        cur_g_y = self.player.gy

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
