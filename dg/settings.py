# strings
INTRO = ["i:Welcome to Wizrad! Find all the elements and break "\
         "the Omni Gem for ultimate POWER",
         "i:(wasd to move, left click to inspect, h for help with other controls)"]

# define some colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BROWN = (168, 104, 50)
LIGHTBLUE = (3, 244, 252)
BLUE = (0, 0, 255)

# Sizes
TILESIZE = 32
GRIDWIDTH = 24
GRIDHEIGHT = 24
WIDTH = TILESIZE * GRIDWIDTH
HEIGHT = TILESIZE * GRIDHEIGHT
TEXTBOX_HEIGHT = 10


# full mape size (for generation)
MAP_WIDTH = 80
MAP_HEIGHT = 60

# Meta Data
FPS = 60
TITLE = "Wizrad"
BGCOLOR = BLACK
# the interval of time in which things happen
TIME_INTERVAL = 0.5

# Viewport
PLAYER_X = int(GRIDWIDTH/2)
PLAYER_Y = int(GRIDHEIGHT/2) - 1  # -1 to account for log window

# Log
VIS_LOG_LINES = 3
TEXT_SIZE = 18
LOG_LINE_DIST = TEXT_SIZE + 5
LOG_X = 0
LOG_Y = int(float(HEIGHT)*0.90)

# Screens (inven, spellmaking, etc)
S_TEXT_SIZE = TEXT_SIZE + 3
S_LINE_DIST = S_TEXT_SIZE + 5
S_X = 0
S_Y = 0

###### Player ######

# starting stats
PLAYER_START_STR = 3
PLAYER_START_CON = 10
PLAYER_START_INT = 3

# stat increase rates (gain RATE% of a point per level)
PLAYER_STR_RATE = 0.5
PLAYER_CON_RATE = 1.5
PLAYER_INT_RATE = 0.5


GODMODE = True

# Movement
SPRINT_DELAY = 1
SPRINT_SPEED = 100

###### Interactables ######

CHEST = "ch"
CHMIN = 20
CHMAX = 30

###### Items ######

HP_POT = 0.4  # heal the player 40%

###### Elements/Spells ######

FIRING_SPEED = 15

# how far a spell must travel (in tiles) before
# it tries to hit things
SPELL_BUFFER = 0

SPELL_SIZE = int(TILESIZE/2)

# Fire
FIRE = "fire"
FCOLOR = RED
FMIN = 20
FMAX = 30
FDAMAGE_RANGE = [1, 7]

# Ice
ICE = "ice"
ICOLOR = BLUE
IMIN = 20
IMAX = 30
IDAMAGE_RANGE = [1, 4]

# color map
E_COLORS = {
    FIRE: FCOLOR,
    ICE: ICOLOR
}

###### Enemies ######

# modifiers for map tracking
# no mods means the enemy is unspawned
SPAWNED = "sp"
DEAD = "x"

# Skeletons
SKELETON = "sk"
SKMIN = 20
SKMAX = 30
SKLIFE = 5
SKDAMAGE_RANGE = [2, 4]
SK_XP = 8   
