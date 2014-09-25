"""
A* Pathfinding implementation.
"""

from math import sqrt
import thread

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

        self.search_done_listener = search_done_listener

        # Node data.
        self.blocked = self._init_d2_lst(False)
        self.parent = self._init_d2_lst()
        self.g_cost = self._init_d2_lst(0)
        self.h_cost = self._init_d2_lst(0)
        self.f_cost = self._init_d2_lst(0)

        for tile in _map.tiles:
            self.blocked[tile[0]+1][tile[1]+1] = True

        for col in range(self.cols+2):
            self.blocked[col][0] = True
            self.blocked[col][self.rows+1] = True

        for row in range(self.rows+2):
            self.blocked[0][row] = True
            self.blocked[self.cols+1][row] = True

    def on_search_done(self, success, path):
        self.search_done_listener(success, path)

    def find_path(self, start, dest):
        thread.start_new_thread(self._find_path, (start, dest))

    def _find_path(self, start, dest):
        """"""
        self.open_lst = set()
        self.closed_lst = set()
        
        path = []
        start_node = (start[0]+1, start[1]+1)
        dest_node = (dest[0]+1, dest[1]+1)
        self.open_lst.add(start_node)

        while len(self.open_lst) != 0:

            lowest_f = 999999
            node_lowest_f = None
            for node in self.open_lst:
                if self.f_cost[node[0]][node[1]] < lowest_f:
                    lowest_f = self.f_cost[node[0]][node[1]]
                    node_lowest_f = node

            curr_node = node_lowest_f

            self.open_lst.remove(curr_node)
            self.closed_lst.add(curr_node)

            if curr_node == dest_node:
                parent = self.parent[curr_node[0]][curr_node[1]]
                
                while parent != start_node:
                    # Retrace path
                    path.append((parent[0]-1, parent[1]-1))
                    parent = self.parent[parent[0]][parent[1]]

                path.append(start)
                self.on_search_done(True, path)
                return 

            self.expand_node(curr_node, dest_node)

        self.on_search_done(False, None)

    def expand_node(self, curr_node, dest_node):
        for neigh in self.get_adjacent(curr_node):

            if self.blocked[neigh[0]][neigh[1]]:
                continue

            if neigh in self.closed_lst:
                continue

            tentative_g = self.g_cost[curr_node[0]][curr_node[1]] + 10

            if neigh in self.open_lst and \
            tentative_g >= self.g_cost[curr_node[0]][curr_node[1]]:
                continue

            self.parent[neigh[0]][neigh[1]] = curr_node
            self.g_cost[neigh[0]][neigh[1]] = tentative_g

            if self.heuristic == MANHATTEN_DISTANCE:
                f = tentative_g + abs(dest_node[0] - neigh[0]) + \
                abs(dest_node[1] - neigh[1])
            elif self.heuristic == EUCLIDIAN_DISTANCE:
                f = tentative_g + sqrt(pow(dest_node[0] - neigh[0], 2) +\
                pow(dest_node[1] - neigh[1], 2))

            self.f_cost[neigh[0]][neigh[1]] = f

            if neigh not in self.open_lst:
                self.open_lst.add(neigh)

    def get_adjacent(self, pos):
        yield (pos[0]-1, pos[1])
        yield (pos[0], pos[1]+1)
        yield (pos[0]+1, pos[1])
        yield (pos[0], pos[1]-1)
        # No diagonal movement
        #~ yield (pos[0]+1, pos[1]-1)
        #~ yield (pos[0]+1, pos[1]+1)
        #~ yield (pos[0]-1, pos[1]+1)
        #~ yield (pos[0]-1, pos[1]-1)

    def _init_d2_lst(self, init_val=None):
        return [[init_val for i in range(self.rows+2)] \
        for i in range(self.cols+2)]
