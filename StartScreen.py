import sys

import pygame as pg

from controls import *
from settings import *


class StartScreen:
    def __init__(self, game):
        self.game = game
        self.playing = False
        fonts_source = pg.font.get_fonts()
        self.font = pg.font.SysFont(fonts_source[0], TEXT_SIZE)

        # button stuff
        self.button_map = [{
            "text_content": "Claim your Destiny",
            "action": "start",
            "x": PLAYER_X,
            "y": PLAYER_Y,
            "color": YELLOW,
            "image": None,
        }]
        self.populate_buttons()

        # title screen stuff
        self.title = "WizRad"

    def start(self):
        self.game.show_startscreen = False

    def populate_buttons(self):
        """
        Gets a list of the buttons on the start screen
        :return:
        """
        for b in self.button_map:
            image = pg.Surface((TILESIZE, TILESIZE))
            image.fill(b["color"])
            b["image"] = image
            r = image.get_rect()
            r.x = b["x"] * TILESIZE
            r.y = b["y"] * TILESIZE
            b["rect"] = r

    def quit(self):
        pg.quit()
        sys.exit()

    def do_action(self, action):
        if action == "start":
            self.start()

    def check_event(self, event):
        if event.type == pg.QUIT:
            self.quit()
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.quit()
            elif MOVE_DOWN(event):
                self.start()
        if INSPECT(event) or INTERACT(event):
            mouse_pos = pg.mouse.get_pos()
            for b in self.button_map:
                try:
                    if b["rect"].collidepoint(mouse_pos):
                        self.do_action(b["action"])
                except:
                    print("NO BUTTON ACTION")

    def drawt(self, screen):
        for b in self.button_map:
            image = b["image"]
            rect = image.get_rect()
            rect.x = b["x"] * TILESIZE
            rect.y = b["y"] * TILESIZE
            screen.blit(image, (rect.x, rect.y))

            text = self.font.render(b["text_content"], True, (255, 255, 255), (0, 0, 0))
            screen.blit(text, (b["rect"].x, b["rect"].y))
