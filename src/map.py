# -*- coding: utf-8 -*-
"""
Map module.
"""

import xml.dom.minidom as dom
import os
from heapq import nsmallest

import pygame
from pygame.locals import SRCALPHA

from utils import str_to_vec, str_to_vec_lst, get_adjacent, grid, \
    m_distance
from constants import SCR_W, ROWS, CELL_SIZE, PANEL_H
from snake import DIRECTIONS


def flood_fill(the_map, map_size, start_pos):
    """
    Slightly improved flood fill algorithm.
    """
    open_lst = set()
    clsd_lst = set()
    filled = set()

    open_lst.add(start_pos)

    while open_lst:
        xpos, ypos = open_lst.pop()

        if the_map[xpos][ypos]:
            filled.add((xpos, ypos))
            clsd_lst.add((xpos, ypos))

            for adjacent in get_adjacent((xpos, ypos), map_size[0],
                                         map_size[1]):
                if adjacent not in clsd_lst:
                    open_lst.add(adjacent)

    return filled


class MapAccessibilityNode(object):
    def __init__(self, tiles, portals):
        self.tiles = tiles
        self.portals = portals

    def get_closest_portal(self, pos):
        ports = [(m_distance(pos, port), port) for port in self.portals]
        return nsmallest(1, ports)[0][1]

    def get_accessible(self):
        return bool(self.portals)

    def contains_target(self, pos, target):
        return pos not in self.tiles and target in self.tiles


class Map(object):

    """
    Represents a simple tile map.
    """

    def __init__(self, game, path):
        self.game = game
        self.tiles = []
        self.spawnpoints = []
        self.portals = {}  # {p1:(p2, dir), p2:(p1, dir)}
        self.islands = []

        size = (SCR_W, ROWS * CELL_SIZE)
        self.tiles_surf = pygame.Surface(size, flags=SRCALPHA)
        self.tiles_surf.fill((0, 0, 0, 0))

        self.load_map(path)

        # Render all tiles onto one surface to save blit calls
        for xpos, ypos in self.tiles:
            tex = self.game.graphics.textures['wall']
            self.tiles_surf.blit(tex,
                                 (xpos * CELL_SIZE, ypos * CELL_SIZE))

    def load_map(self, path):
        doc = dom.parse(path)
        maptag = doc.firstChild

        self.name = os.path.splitext(os.path.basename(path))[0]
        self.description = maptag.getAttribute('description')
        self.size_str = maptag.getAttribute('size')
        self.width = int(self.size_str.split('x')[0])
        self.height = int(self.size_str.split('x')[1])

        for node in maptag.childNodes:
            if node.nodeName == 'Tiles':
                self.tiles = str_to_vec_lst(node.firstChild.data)
            elif node.nodeName == 'Spawnpoints':
                self.spawnpoints = str_to_vec_lst(node.firstChild.data)
            elif node.nodeName == 'Portals':
                for portal_node in node.childNodes:
                    if portal_node.nodeName == 'Portal':
                        # Needs refactoring/improvement
                        point1 = point2 = p1_dir = p2_dir = None
                        for p_node in portal_node.childNodes:
                            if p_node.nodeName == 'p1':
                                point1 = \
                                    str_to_vec(p_node.firstChild.data)
                                p1_dir = \
                                    DIRECTIONS[
                                        p_node.getAttribute('dir')]
                            elif p_node.nodeName == 'p2':
                                point2 = \
                                    str_to_vec(p_node.firstChild.data)
                                p2_dir = \
                                    DIRECTIONS[
                                        p_node.getAttribute('dir')]
                            if point1 is not None and point2 is not None:
                                self.portals.update(
                                    {point1: (point2, p2_dir),
                                     point2: (point1, p1_dir)})

        set_of_tiles = set(grid(self.width, self.height))
        set_of_tiles -= set(self.tiles)

        accessibility_map = [None] * self.width
        accessibility_map = [[None] * self.height for _ in
                             accessibility_map]

        for xpos, ypos in grid(self.width, self.height):
            accessibility_map[xpos][ypos] = (xpos, ypos) not in self.tiles

        while set_of_tiles:
            pos = set_of_tiles.pop()
            tiles = flood_fill(accessibility_map,
                               (self.width, self.height), pos)
            portals = []

            for portal in self.portals:
                if (self.portals[portal][0] in tiles and
                            portal not in tiles):
                    portals.append(portal)

            self.islands.append(MapAccessibilityNode(tiles, portals))

            set_of_tiles -= tiles

    def wrap_around(self, obj):
        """Wrap obj around the map."""
        xpos, ypos = obj
        if xpos < 0:
            obj = (self.width-1, ypos)
        if xpos > self.width-1:
            obj = (0, ypos)
        if ypos < 0:
            obj = (xpos, self.height-1)
        if ypos > self.height-1:
            obj = (xpos, 0)
        return obj

    def get_spawnpoint(self):
        """Return  random, unblocked spawnpoint."""
        return self.game.randomizer.choice([spawnpoint for spawnpoint in
                                       self.spawnpoints
                                       if self.sp_unblocked(spawnpoint)])

    def sp_unblocked(self, spawnpoint):
        """Determine if a spawnpoint is blocked."""
        return len(self.game.curr_state.mode.spatialhash[spawnpoint]) == 1

    def on_edge(self, pos):
        """Determines if pos is on the edge of the map."""
        return pos[0] == 0 or pos[0] == self.width-1 or \
            pos[1] == 0 or pos[1] == self.height-1

    def randpos(self):
        """Return random position."""
        while True:
            pos = (self.game.randomizer.randint(1, self.width-1),
                   self.game.randomizer.randint(1, self.height-1))
            if (pos not in self.game.curr_state.mode.spatialhash and
                        pos not in self.tiles):
                return pos

    def draw(self):
        """Draw map."""
        self.game.screen.blit(self.tiles_surf, (0, PANEL_H))

        for spawnpoint in self.spawnpoints:
            self.game.graphics.draw('spawnpoint', spawnpoint)

        for portal in self.portals.values():
            self.game.graphics.draw('portal', portal[0])
