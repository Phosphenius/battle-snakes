# -*- coding: utf-8 -*-

from heapq import heappush, heappop


class Node(object):
    def __init__(self, pos, blocked=False, penalty=0):
        self.pos = pos
        self._gcost = penalty
        self._hcost = 0
        self._fcost = self._gcost + self._hcost
        self.blocked = blocked
        self.parent = None

    def get_fcost(self):
        return self._fcost

    def get_gcost(self):
        return self._gcost

    def set_gh(self, gcost, hcost):
        self._gcost = gcost
        self._hcost = hcost
        self._fcost = self._gcost + self._hcost

    def __cmp__(self, other):
        return cmp(self._fcost, other.get_fcost())

    def __eq__(self, other):
        return self.pos == other.pos


class AStar(object):
    """
    A* implementation, as simple as it gets.
    """
    def __init__(self, cols, rows, blocked):
        self.rows = rows
        self.cols = cols
        self.blocked = set(blocked)
        self.open_lst = list()
        self.clsd_lst = set()
        self.nodes = [None] * self.cols
        self.nodes = [[None] * self.rows for _ in self.nodes]
        self.reinit()

    def reinit(self):
        self.open_lst = list()
        self.clsd_lst = set()
        self.nodes = [None] * self.cols
        self.nodes = [[None] * self.rows for _ in self.nodes]

        for xpos in range(self.cols):
            for ypos in range(self.rows):
                pos = (xpos, ypos)
                self.nodes[xpos][ypos] = Node(pos, pos in self.blocked)

    def find_path(self, start_pos, dest_pos):
        self.reinit()
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

            self.expand_node(curr_node, dest_node)

        return path

    def expand_node(self, curr_node, dest_node):
        for adjacent in self.get_adjacent(curr_node):
            if adjacent.blocked or adjacent in self.clsd_lst:
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
        pos = node.pos
        if pos[0] > 0:
            yield self.nodes[pos[0] - 1][pos[1]]
        if pos[1] < self.rows - 1:
            yield self.nodes[pos[0]][pos[1] + 1]
        if pos[0] < self.cols - 1:
            yield self.nodes[pos[0] + 1][pos[1]]
        if pos[1] > 0:
            yield self.nodes[pos[0]][pos[1] - 1]
