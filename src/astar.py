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
    def __init__(self, tmap):
        self.rows = tmap.height
        self.cols = tmap.width
        self.blocked = set(tmap.tiles)
        self.tilemap = tmap
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

        return None

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
        xpos, ypos = node.pos
        portals = self.tilemap.portals

        if xpos > 0:
            new_xpos = xpos - 1
            if (new_xpos, ypos) in portals:
                node_x = portals[(new_xpos, ypos)][0][0] + \
                         portals[(new_xpos, ypos)][1][0]
                node_y = portals[(new_xpos, ypos)][0][1] + \
                         portals[(new_xpos, ypos)][1][1]
                yield self.nodes[node_x][node_y]
            else:
                yield self.nodes[new_xpos][ypos]
        else:
            yield self.nodes[self.cols-1][ypos]

        if ypos < self.rows - 1:
            new_ypos = ypos + 1
            if (xpos, new_ypos) in portals:
                node_x = portals[(xpos, new_ypos)][0][0] + \
                         portals[(xpos, new_ypos)][1][0]
                node_y = portals[(xpos, new_ypos)][0][1] + \
                         portals[(xpos, new_ypos)][1][1]
                yield self.nodes[node_x][node_y]
            else:
                yield self.nodes[xpos][new_ypos]
        else:
            yield self.nodes[xpos][0]

        if xpos < self.cols - 1:
            new_xpos = xpos + 1
            if (new_xpos, ypos) in portals:
                node_x = portals[(new_xpos, ypos)][0][0] + \
                         portals[(new_xpos, ypos)][1][0]
                node_y = portals[(new_xpos, ypos)][0][1] + \
                         portals[(new_xpos, ypos)][1][1]
                yield self.nodes[node_x][node_y]
            else:
                yield self.nodes[xpos + 1][ypos]
        else:
            yield self.nodes[0][ypos]

        if ypos > 0:
            new_ypos = ypos - 1
            if (xpos, new_ypos) in portals:
                node_x = portals[(xpos, new_ypos)][0][0] + \
                         portals[(xpos, new_ypos)][1][0]
                node_y = portals[(xpos, new_ypos)][0][1] + \
                         portals[(xpos, new_ypos)][1][1]
                yield self.nodes[node_x][node_y]
            else:
                yield self.nodes[xpos][ypos - 1]
        else:
            yield self.nodes[xpos][self.rows-1]
