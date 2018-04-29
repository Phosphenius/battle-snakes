# -*- coding: utf-8 -*-

from heapq import heappush, heappop
from collections import defaultdict

from utils import add_vecs, sub_vecs, get_adjacent


WALL_PENALTY_MAX_SPREAD = 3


class Node(object):
    def __init__(self, pos, blocked=False, penalty=0):
        self.pos = pos
        self._gcost = 0
        self._hcost = 0
        self._fcost = self._gcost + self._hcost
        self.penalty = penalty
        self.blocked = blocked
        self.parent = None

    def get_fcost(self):
        return self._fcost

    def get_gcost(self):
        return self._gcost

    def set_gh(self, gcost, hcost):
        self._gcost = gcost + self.penalty
        self._hcost = hcost
        self._fcost = self._gcost + self._hcost

    def __cmp__(self, other):
        return cmp(self._fcost, other.get_fcost())

    def __eq__(self, other):
        return self.pos == other.pos


class Pathfinder(object):
    """
    """
    def __init__(self, game):
        self.game = game
        self.astar = AStar(game.tilemap)

    def find_path(self, start_pos, dest_pos):
        tilemap = self.game.tilemap

        for island in tilemap.islands:
            if island.contains_target(start_pos, dest_pos):
                portal1 = island.get_closest_portal(start_pos)
                portal2 = tilemap.portals[portal1][0]
                offset2 = add_vecs(portal2, tilemap.portals[portal1][1])

                blocked = set(tilemap.portals.keys())
                blocked -= {portal1}

                path1 = self.astar.find_path(start_pos, portal1)
                path2 = self.astar.find_path(offset2, dest_pos, blocked)

                path2.append(offset2)

                return path2 + path1

        blocked = set(tilemap.portals.keys())

        return self.astar.find_path(start_pos, dest_pos, blocked)


class AStar(object):
    """
    A* implementation, as simple as it gets.
    """
    def __init__(self, tilemap):
        self.rows = tilemap.height
        self.cols = tilemap.width
        self.blocked = set(tilemap.tiles)
        self.tilemap = tilemap
        self.open_lst = list()
        self.clsd_lst = set()
        self.nodes = [None] * self.cols
        self.nodes = [[None] * self.rows for _ in self.nodes]

        penalty = defaultdict(int)

        for tile in tilemap.tiles:
            for adjacent in get_adjacent(tile, self.cols, self.rows):
                if adjacent in self.blocked:
                    continue

                spread_dir = sub_vecs(adjacent, tile)
                spread_count = 1
                spread = add_vecs(tile, spread_dir)

                while (spread not in tilemap.tiles
                       and not on_edge(spread)
                       and spread_count < WALL_PENALTY_MAX_SPREAD):
                    penalty[spread] += 12 / spread_count

                    spread = add_vecs(spread, spread_dir)
                    spread_count += 1

        for xpos in range(self.cols):
            for ypos in range(self.rows):
                pos = (xpos, ypos)
                pen = penalty.get((xpos, ypos), 0)
                self.nodes[xpos][ypos] = Node(pos, pos in self.blocked, pen)

    def find_path(self, start_pos, dest_pos, blocked=None):
        self.open_lst = list()
        self.clsd_lst = set()
        path = []
        start_node = Node(start_pos)
        dest_node = Node(dest_pos)

        heappush(self.open_lst, start_node)

        while len(self.open_lst) != 0:
            curr_node = heappop(self.open_lst)
            self.clsd_lst.add(curr_node)

            if curr_node == dest_node:
                parent = curr_node.parent

                while parent != start_node:
                    path.append(parent.pos)
                    parent = parent.parent

                return path

            if blocked:
                self.expand_node(curr_node, dest_node, blocked)
            else:
                self.expand_node(curr_node, dest_node, [])

        return None

    def expand_node(self, curr_node, dest_node, blocked):
        for adjacent in self.get_adjacent(curr_node):
            if (adjacent.blocked or adjacent in self.clsd_lst or
                    adjacent.pos in blocked):
                continue

            tentative_g = adjacent.get_gcost()

            if adjacent in self.open_lst and \
                    tentative_g >= adjacent.get_gcost():
                continue

            adjacent.parent = curr_node

            heuristics = abs(dest_node.pos[0] - adjacent.pos[0]) + \
                abs(dest_node.pos[1] - adjacent.pos[1])

            adjacent.set_gh(tentative_g, heuristics)

            if adjacent not in self.open_lst:
                heappush(self.open_lst, adjacent)

    def get_adjacent(self, node):
        xpos, ypos = node.pos

        if xpos > 0:
            yield self.nodes[xpos - 1][ypos]
        else:
            yield self.nodes[self.cols-1][ypos]

        if ypos < self.rows - 1:
            yield self.nodes[xpos][ypos + 1]
        else:
            yield self.nodes[xpos][0]

        if xpos < self.cols - 1:
            yield self.nodes[xpos + 1][ypos]
        else:
            yield self.nodes[0][ypos]

        if ypos > 0:
            yield self.nodes[xpos][ypos - 1]
        else:
            yield self.nodes[xpos][self.rows-1]
