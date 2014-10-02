"""
A* Pathfinding implementation.
"""

from math import sqrt
import thread
from collections import defaultdict

from utils import add_vecs

# Heuristics
MANHATTEN_DISTANCE = 0
EUCLIDIAN_DISTANCE = 1

class Pathfinder(object):
    """
    Pathfinder using the A* algorithm.

    Supports Manhatten method and Euclidian Distance as heuristic functions.
    """
    def __init__(self, _map, heuristic, search_done_listener):
        self.heuristic = heuristic

        self.open_lst = set()
        self.closed_lst = set()

        self.cols = _map.width
        self.rows = _map.height
        self.portals = _map.portals

        self.search_done_listener = search_done_listener

        self.blocked = defaultdict(bool)
        self.parent = defaultdict(tuple)
        self.g_cost = defaultdict(int)
        self.h_cost = defaultdict(int)
        self.f_cost = defaultdict(int)

        for tile in _map.tiles:
            self.blocked[tile] = True

    def on_search_done(self, success, path):
        self.search_done_listener(success, path)

    def find_path(self, start, dest):
        thread.start_new_thread(self._find_path, (start, dest))

    def _find_path(self, start, dest):
        """"""
        self.open_lst = set()
        self.closed_lst = set()
        
        path = []
        self.open_lst.add(start)

        while len(self.open_lst) != 0:

            lowest_f = 999999
            node_lowest_f = None
            for node in self.open_lst:
                if self.f_cost[node] < lowest_f:
                    lowest_f = self.f_cost[node]
                    node_lowest_f = node

            curr_node = node_lowest_f

            self.open_lst.remove(curr_node)
            self.closed_lst.add(curr_node)

            if curr_node == dest:
                parent = self.parent[curr_node]
                
                while parent != start:
                    # Retrace path
                    path.append(parent)
                    parent = self.parent[parent]

                path = list(reversed(path))
                path.append(dest)
                self.on_search_done(True, path)
                return 

            self.expand_node(curr_node, dest)

        self.on_search_done(False, None)

    def expand_node(self, curr_node, dest):
        for neigh in self.get_adjacent(curr_node):

            if self.blocked[neigh]:
                continue

            if neigh in self.closed_lst:
                continue

            tentative_g = self.g_cost[curr_node] + 10

            if neigh in self.open_lst and \
            tentative_g >= self.g_cost[curr_node]:
                continue

            self.parent[neigh] = curr_node
            self.g_cost[neigh] = tentative_g

            if self.heuristic == MANHATTEN_DISTANCE:
                f = tentative_g + abs(dest[0] - neigh[0]) + \
                abs(dest[1] - neigh[1])
            elif self.heuristic == EUCLIDIAN_DISTANCE:
                f = tentative_g + sqrt(pow(dest[0] - neigh[0], 2) + \
                pow(dest[1] - neigh[1], 2))

            self.f_cost[neigh] = f

            if neigh not in self.open_lst:
                self.open_lst.add(neigh)

    def get_adjacent(self, pos):
        if pos[0] > 0: 
            if (pos[0]-1, pos[1]) not in self.portals:
                yield (pos[0]-1, pos[1])  
            else: 
                yield add_vecs(self.portals[(pos[0]-1, pos[1])][0],
                               self.portals[(pos[0]-1, pos[1])][1])
        else:
            yield (self.cols-1, pos[1])
        if pos[1] < self.rows-1:
            if (pos[0], pos[1]+1) not in self.portals:
                yield (pos[0], pos[1]+1)  
            else:
                yield add_vecs(self.portals[(pos[0], pos[1]+1)][0],
                               self.portals[(pos[0], pos[1]+1)][1])
        else:
            yield (pos[0], 0)
        if pos[0] < self.cols-1:
            if (pos[0]+1, pos[1]) not in self.portals:
                yield (pos[0]+1, pos[1])  
            else:
                yield add_vecs(self.portals[(pos[0]+1, pos[1])][0],
                               self.portals[(pos[0]+1, pos[1])][1])
        else:
            yield (0, pos[1])
        if pos[1] > 0:
            if (pos[0], pos[1]-1) not in self.portals:
                yield (pos[0], pos[1]-1)
            else: 
                yield add_vecs(self.portals[(pos[0], pos[1]-1)][0],
                               self.portals[(pos[0], pos[1]-1)][1])
        else:
            yield (pos[0], self.rows-1)
