# -*- coding: utf-8 -*-

INVINCIBILITY_BLINK_RATE = 0.1

# Speed
INIT_SPEED = 10
MIN_SPEED = INIT_SPEED
MAX_SPEED = 16.

# Speed boost
MAX_BOOST = 5000
INIT_BOOST = MAX_BOOST
BOOST_SPEED = 24.
BOOST_GAIN = 260
BOOST_COST = 1735

# Health
INIT_LIFES = 3
MAX_LIFES = 10
MAX_HITPOINTS = 500


# Grid & size
CELL_SIZE = 10
ROWS = 64
COLS = 128
PANEL_H = 42
SCR_W = COLS * CELL_SIZE
SCR_H = (ROWS * CELL_SIZE) + PANEL_H

# Tags
PWRUP_TAG = '#powerup'
PORTAL_TAG = '#portal'
WALL_TAG = '#wall'
SPAWNPOINT_TAG = '#spawnpoint'
SHOT_TAG = '#shot'

# Colors
CORNFLOWERBLUE = (100, 149, 237) #6495ED
BLACK = (0, 0, 0) #000000
WHITE = (255, 255, 255) #FFFFFF
RED = (255, 0, 0)  #FF0000
LIME = (0, 255, 0) #00FF00
BLUE = (0, 0, 255) #0000FF
YELLOW = (255, 255, 0) #FFFF00
CYAN = (0, 255, 255) #00FFFF
MAGENTA = (255, 0, 255) #FF00FF
SILVER = (192, 192, 192) #C0C0C0
GRAY = (128, 128, 128) #808080
MAROON = (128, 0, 0) #800000
OLIVE = (128, 128, 0) #808000
GREEN = (0, 128, 0) #008000
PURPLE = (128, 0, 128) #800080
TEAL = (0, 128, 128) #008080
NAVY = (0, 0, 128) #000080
DARK_PURPLE = (128, 0, 128) #800080
DARK_BLUE = (0, 0, 160) #0000A0
ORANGE = (255, 165, 0) #2C3539
GUN_METAL = (44, 53, 57) #FFA500

COLORS = {
          'cornflowerblue': CORNFLOWERBLUE,
          'black': BLACK,
          'white': WHITE,
          'red': RED,
          'lime': LIME,
          'blue': BLUE,
          'yellow': YELLOW,
          'cyan': CYAN,
          'magenta': MAGENTA,
          'silver': SILVER,
          'gray': GRAY,
          'maroon': MAROON,
          'olive': OLIVE,
          'green': GREEN,
          'purple': PURPLE,
          'teal': TEAL,
          'navy': NAVY,
          'purple': PURPLE,
          'dark_blue': DARK_BLUE,
          'orange': ORANGE,
          'gun_metal': GUN_METAL
          }

# Base widget default values
WIDGET_HEIGHT = 50
WIDGET_BG_COLOR = GRAY
WIDGET_BORDER_THICKNESS = 3
WIDGET_BORDER_COLOR = RED
WIDGET_BORDER_FOCUS_COLOR = ORANGE

# Base widget constants
WIDGET_DISABLED_BORDER_COLOR = GUN_METAL

# Text widget default values
TEXT_WIDGET_TEXT_COLOR = BLACK
TEXT_WIDGET_TEXT_COLOR_FOCUS = WHITE

# Text widget constants
TEXT_WIDGET_DISABLED_TEXT_COLOR = SILVER

# Label default values
LABEL_WIDGET_TEXT_COLOR = DARK_BLUE
LABEL_WIDGET_BORDER_COLOR = PURPLE

# Cycle button constants
TRIANGLE_WIDTH = 25

# Stack panel default values
STACK_PANEL_PAD_Y = 10

