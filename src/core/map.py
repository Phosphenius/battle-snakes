# -*- coding: utf-8 -*-

import json
from zipfile import ZipFile
import os
from heapq import nsmallest

from utils import (vec_lst_to_str, str_to_vec_lst, str_to_vec,
                   get_adjacent, m_distance, grid)
from constants import COLS, ROWS


# Defaults for tile map meta data
DEFAULT_TITLE = 'untitled'
DEFAULT_DESC = 'no description'


def wrap_around(pos):
    """Wrap obj around the map."""
    pos_x, pos_y = pos
    if pos_x < 0:
        pos = (COLS - 1, pos_y)
    if pos_x > COLS - 1:
        pos = (0, pos_y)
    if pos_y < 0:
        pos = (pos_x, ROWS - 1)
    if pos_y > ROWS - 1:
        pos = (pos_x, 0)
    return pos


def on_edge(pos):
    """Determines if pos is on the edge of the map."""
    return (pos[0] == 0 or pos[0] == COLS-1 or
            pos[1] == 0 or pos[1] == ROWS-1)


def flood_fill(the_map, map_size, start_pos):
    """
    Slightly improved flood fill algorithm.
    """
    # Using sets for faster look-up
    open_lst = set()
    closed_lst = set()
    filled = set()

    open_lst.add(start_pos)

    while open_lst:
        pos_x, pos_y = open_lst.pop()

        if the_map[pos_x][pos_y]:
            filled.add((pos_x, pos_y))
            closed_lst.add((pos_x, pos_y))

            for adjacent in get_adjacent((pos_x, pos_y), map_size[0],
                                         map_size[1]):
                if adjacent not in closed_lst:
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


class TileMapBase(object):
    """
    Holds Tile Map data and provides basic funtionality like drawing
    """
    def __init__(self, gfx_manager, filepath=''):
        config = {}
        tiles_raw = ''
        blocked_raw = ''

        if os.path.exists(filepath):
            with ZipFile(filepath) as mapzip:
                with mapzip.open('meta.json', 'r') as json_file:
                    config = json.load(json_file)

                with mapzip.open('tiles', 'r') as tiles_file:
                    tiles_raw = tiles_file.read()

                with mapzip.open('blocked', 'r') as blocked_file:
                    blocked_raw = blocked_file.read()

        self.gfx_manager = gfx_manager
        self.title = config.get('title', DEFAULT_TITLE)
        self.description = config.get('description', DEFAULT_DESC)
        self.textures = config.get('textures', {})
        self.textures = {int(tid): tex for (tid, tex) in self.textures.items()}
        self.spawnpoints = [tuple(sp) for sp in config.get('spawnpoints', [])]
        self.portals = {}
        self.tiles = [0] * COLS
        self.tiles = [[0] * ROWS for _ in self.tiles]
        self.blocked = set(str_to_vec_lst(blocked_raw))
        self.islands = []

        for p1, p2 in config.get('portals', {}).items():
            self.portals[str_to_vec(p1)] = (tuple(p2[0]), tuple(p2[1]))

        if tiles_raw:
            for pos_y, line in enumerate(tiles_raw.strip().split('\n')):
                for pos_x, val in enumerate(line.strip().split(' ')):
                    self.tiles[pos_x][pos_y] = int(val)

        set_of_tiles = set(grid(COLS, ROWS))
        set_of_tiles -= self.blocked

        accessibility_map = [None] * COLS
        accessibility_map = [[None] * ROWS for _ in
                             accessibility_map]

        for pos_x, pos_y in grid(COLS, ROWS):
            accessibility_map[pos_x][pos_y] = \
                (pos_x, pos_y) not in self.blocked

        while set_of_tiles:
            pos = set_of_tiles.pop()
            tiles = flood_fill(accessibility_map, (COLS, ROWS), pos)
            portals = []

            for portal in self.portals:
                if (self.portals[portal][0] in tiles and
                        portal not in tiles):
                    portals.append(portal)

            self.islands.append(
                MapAccessibilityNode(tiles, portals))

            set_of_tiles -= tiles

    def add_portal(self, p1, p2, p1_dir, p2_dir):
        """
        Add a portal to the map. A portal is a connection between
        2 locations on the map. Moving through a portal changes
        direction
        :param p1: First location of the portal
        :param p2: Second location of the portal
        :param p1_dir: Direction when leaving the first portal
        :param p2_dir: Direction when leaving the second portal
        :return:
        """
        self.portals[p1] = (p2, p1_dir)
        self.portals[p2] = (p1, p2_dir)

    def write_to_file(self, file_path):
        """
        Write map to a zip file containing metadata as a json and the
        actual map data as a simple text file
        :param file_path: path to the file
        :return:
        """
        config = {'title': self.title, 'description': self.description}
        config['textures'] = self.textures
        config['spawnpoints'] = self.spawnpoints
        config['portals'] = {'{0}:{1}'.format(p1[0], p1[1]): p2 for
                             (p1, p2) in self.portals.items()}

        with ZipFile(file_path, 'w') as mapzip:
            with open('meta.json', 'w') as json_file:
                json.dump(config, json_file)

            with open('tiles', 'w') as tiles_file:
                for pos_y in range(ROWS):
                    for pos_x in range(COLS):
                        fmt_str = '{0}' if pos_x == (COLS-1) else '{0} '

                        tiles_file.write(fmt_str.format(
                            self.tiles[pos_x][pos_y]))
                    tiles_file.write('\n')

            with open('blocked', 'w') as blocked_file:
                if self.blocked:
                    blocked_file.write(vec_lst_to_str(self.blocked))

            for file in ('meta.json', 'tiles', 'blocked'):
                mapzip.write(file)
                os.remove(file)

    def draw(self):
        """
        Draw tile map, skipping tiles which have not texture assigned
        :return:
        """
        for xpos in range(COLS):
            for ypos in range(ROWS):
                tile = self.tiles[xpos][ypos]

                if tile not in self.textures:
                    continue

                self.gfx_manager.draw(self.textures[tile],
                                      (xpos, ypos))

        for spawnpoint in self.spawnpoints:
            self.gfx_manager.draw('spawnpoint', spawnpoint)

        for portal in self.portals.values():
            self.gfx_manager.draw('portal', portal[0])


class TileMap(TileMapBase):
    """
    Extends BaseTileMap with functions for in game use
    """
    def __init__(self, game, filepath):
        self.game = game
        TileMapBase.__init__(self, game.graphics, filepath)

    def get_spawnpoint(self):
        """Return  random, unblocked spawnpoint."""
        unblocked_sp = [spawnpoint for spawnpoint in self.spawnpoints if
                        self.sp_unblocked(spawnpoint)]
        return self.game.randomizer.choice(unblocked_sp)

    def sp_unblocked(self, spawnpoint):
        """Determine if a spawnpoint is blocked."""
        return len(self.game.curr_state.mode.spatialhash[spawnpoint]) == 1

    def randpos(self):
        """Return random position."""
        while True:
            pos = (self.game.randomizer.randint(1, COLS-1),
                   self.game.randomizer.randint(1, ROWS-1))
            if (pos not in self.game.curr_state.mode.spatialhash and
                    pos not in self.tiles):
                return pos
