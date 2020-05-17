# strings
INTRO = ["i:Welcome to Wizrad! Find all the elements and break "\
         "the Omni Gem for ultimate POWER",
         "i:(wasd to move, left click to inspect)"]

# define some colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Sizes
WIDTH = 512   # TILESIZE * 32
HEIGHT = 512  # TILESIZE * 32
TEXTBOX_HEIGHT = 10
PLAYER_X = 8
PLAYER_Y = 8

# full mape size (for generation)
MAP_WIDTH = 80
MAP_HEIGHT = 60

# Meta Data
FPS = 60
TITLE = "Wizrad"
BGCOLOR = DARKGREY

# Viewport (camera) sizes (32 wide, 24 high)
TILESIZE = 32
GRIDWIDTH = int(WIDTH / TILESIZE)
GRIDHEIGHT = int(HEIGHT / TILESIZE)

# Log
VIS_LOG_LINES = 3
TEXT_SIZE = 12
LOG_LINE_DIST = TEXT_SIZE + 5
LOG_X = 0
LOG_Y = int(float(HEIGHT)*0.90)

# Movement
SPRINT_DELAY = 1
SPRINT_SPEED = 100

###### Elements/Spells ######

FIRING_SPEED = 15

# Fire
FIRE = "f"
FMIN = 20
FMAX = 30