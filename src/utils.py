# -*- coding: utf-8 -*-
"""Contains useful functions/classes"""

from math import hypot


def get_adjacent(pos, cols, rows):
    """Get adjacent tiles in a grid."""
    if pos[0] > 0:
        yield (pos[0]-1, pos[1])
    if pos[1] < rows-1:
        yield (pos[0], pos[1]+1)
    if pos[0] < cols-1:
        yield (pos[0]+1, pos[1])
    if pos[1] > 0:
        yield (pos[0], pos[1]-1)


def add_vecs(vec1, vec2):
    """Add vectors."""
    return (vec1[0] + vec2[0], vec1[1] + vec2[1])


def sub_vecs(vec1, vec2):
    """Sub vectors."""
    return (vec1[0] - vec2[0], vec1[1] - vec2[1])


def mul_vec(vec, scalar):
    """Multiply vector with scalar."""
    return (vec[0] * scalar, vec[1] * scalar)


def m_distance(vec1, vec2):
    """Manhatten Distance between vec1 and vec2."""
    return abs(vec1[0] - vec2[0]) + abs(vec1[1] - vec2[1])


def distance(vec1, vec2):
    """Euclidian Distance between vec1 and vec2."""
    return hypot(vec1[0] - vec2[0], vec1[1] - vec2[1])


def normalize(vec):
    """
    Normalize vector. Note that this functions returns an int vector.
    """
    length = hypot(vec[0], vec[1])
    return int(round(vec[0] / length)), int(round(vec[1] / length))


def str_to_vec(data):
    """Convert string rep. of a vector to tuple."""
    return tuple(int(i) for i in data.strip().split(':'))


def str_to_vec_lst(data):
    """Convert string rep. of vector list to tuple list."""
    veclst = []
    for entry in data.strip().split(';'):
        veclst.append(str_to_vec(entry))
    return veclst


def vec_lst_to_str(lst):
    """Convert list of tuples to string rep."""
    str_rep = ''
    for i, vec in enumerate(lst):
        sep = ';' if i != 0 else ''
        str_rep += '{0}{1}:{2}'.format(sep, vec[0], vec[1])
    return str_rep


class Timer(object):

    """
    Simple infinite timer.

    Note: Timer cannot be stopped.
    """

    def __init__(self, intervall, tick, delay=0, running=False):
        self.intervall = intervall
        self.tick = tick
        self.elapsed_t = 0.
        self.delay = delay
        self.running = running if self.delay == 0 else False

    def start(self, delay=0):
        """Start timer."""
        if delay != 0:
            self.delay = delay
            return
        self.running = True
        self.elapsed_t = 0.

    def update(self, delta_time):
        """Update timer."""
        if self.running:
            self.elapsed_t += delta_time
            if self.elapsed_t >= self.intervall:
                self.elapsed_t -= self.intervall
                # On tick
                if self.tick is not None:
                    self.tick()
                else:
                    raise Exception('No Tick-event handler!')
        elif self.delay > 0.:
            self.elapsed_t += delta_time
            if self.elapsed_t >= self.delay:
                self.running = True
                self.elapsed_t = 0.
