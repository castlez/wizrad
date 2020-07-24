DEBUG=True

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
PINK = (255, 51, 204)

# Sizes
TILESIZE = 32
GRIDWIDTH = 24
GRIDHEIGHT = 24
WIDTH = TILESIZE * GRIDWIDTH
HEIGHT = TILESIZE * GRIDHEIGHT
TEXTBOX_HEIGHT = 10


# full map size (for generation)
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
PLAYER = "@"
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

# current god mode (also starting godmode)
GODMODE = False

# Movement
SPRINT_DELAY = 1
SPRINT_SPEED = 100

###### Interactables ######

CHEST = "C"
CHMIN = 5
CHMAX = 10

###### Items ######

HP_POT = 0.4  # heal the player 40%
CRYSTAL = "+"  # the point of the entire game, get this and win instantly

###### Objects (not alive) ######
WALL = 1
FLOOR = "."

###### Elements/Spells ######

FIRING_SPEED = 15

# how far a spell must travel (in tiles) before
# it tries to hit things
SPELL_BUFFER = 0

SPELL_SIZE = int(TILESIZE/2)

# Fire
FIRE = "F"
FDOOR = "FD" 
FCOLOR = RED
FMIN = 20
FMAX = 30
FDAMAGE_RANGE = [1, 7]

# Ice
ICE = "i"
IDOOR = "ID"
ICOLOR = BLUE
IMIN = 20
IMAX = 30
IDAMAGE_RANGE = [1, 4]

# acid
ACID = "a"
ADOOR = "AD"
ACOLOR = GREEN
AMIN = 20
AMAX = 30
ADAMAGE_RANGE = [1, 3]

# electricity
ELEC = "e"
EDOOR = "ED"
ECOLOR = LIGHTBLUE
EMIN = 20
EMAX = 30
EDAMAGE_RANGE = [3, 3]

# Door element map
DEM = {
    FDOOR: FIRE,
    IDOOR: ICE,
    EDOOR: ELEC,
    ADOOR: ACID
}

# color map
E_COLORS = {
    FIRE: FCOLOR,
    ICE: ICOLOR,
    ACID: ACOLOR,
    ELEC: ECOLOR
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


