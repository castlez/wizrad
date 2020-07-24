import pygame as pg

INVENTORY = lambda event: event.key == pg.K_i
ICHECK = lambda event: event.type == pg.MOUSEBUTTONUP and event.button == 1
ISELECT = lambda event: event.type == pg.MOUSEBUTTONUP and event.button == 3
QUIT_GAME = lambda event: event.key == pg.K_ESCAPE
SAVE_MAP = lambda event: event.key == pg.K_m
MOVE_LEFT = lambda event: event.key == pg.K_a
MOVE_RIGHT = lambda event: event.key == pg.K_d
MOVE_UP = lambda event: event.key == pg.K_w
MOVE_DOWN = lambda event: event.key == pg.K_s
FIRE_SPELL = lambda event: event.key == pg.K_SPACE
DO_TICK = lambda event: event.key == pg.K_RETURN
USE_ITEM = lambda event: event.key == pg.K_RSHIFT or event.key == pg.K_LSHIFT

SHOW_GRID = lambda event: event.key == pg.K_g
GODMODE = lambda event: event.key == pg.K_l
PRINT_STATS = lambda event: event.key == pg.K_o
LOG_SCROLL_UP = lambda event: event.key == pg.K_DOWN
LOG_SCROLL_DOWN = lambda event: event.key == pg.K_UP
HELP = lambda event: event.key == pg.K_h
INSPECT = lambda event: event.type == pg.MOUSEBUTTONUP and event.button == 1
INTERACT = lambda event: event.type == pg.MOUSEBUTTONUP and event.button == 3