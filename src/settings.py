# -*- coding: utf-8 -*-
"""Settings."""

from colors import RED, BLUE

ID_TO_COLOR = {0: RED, 1: BLUE}

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
INIT_LIFES = 8
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
