#!/usr/bin/python2
# -*- coding: UTF-8 -*-

"""
Simple Potential Field implementation.
"""

from copy import copy

from utils import distance, get_adjacent


class PotentialField(object):

    """
    Implementation of a Potential Field. Not complete, but it works for now.
    Repelling fields have yet to be implemented, though.
    """

    def __init__(self, field, width, height):
        """
        Initialize Potential Field from a 2D list (list containing lists).
        """
        self.width = width
        self.height = height
        self.field = field

    @staticmethod
    def create(width, height, *args):
        """
        Create Potential Field from points/vectors in *args.
        This adds all the fields projected by the points/vectors into one,
        single field. Of course a single point/vector can be used as an
        argument, too.
        """
        field = [None] * width
        # Can these two loops be combined into one?
        for xpos in range(width):
            field[xpos] = [0] * height
        #
        for pos in args:
            for xpos in range(width):
                for ypos in range(height):
                    field[xpos][ypos] += distance((xpos, ypos), pos)

        return PotentialField(field, width, height)

    def __add__(self, other):
        """Add to Potential Fields. This yields a new instance."""
        if self.width != other.width or self.height != other.height:
            raise Exception('Fields must not have different sizes!')

        result = copy(self)

        for xpos in range(self.width):
            for ypos in range(self.height):
                result.field[xpos][ypos] += other.field[xpos][ypos]

        return result

    def get_next(self, pos):
        """Get the next, cheapest tile/point in the field adjacent to 'pos'."""
        return min([(self.field[tile[0]][tile[1]], tile) for tile in
                    get_adjacent(pos, self.width, self.height)])[1]
