# -*- coding: utf-8 -*-


"""
Base functionality for tile map editor tools
"""


import colors
import pygame
import fsm
from mapedit import LEFT_MOUSE_BUTTON
import constants


SELECTION_DEFAULT_COLOR = colors.YELLOW


class BaseToolState(fsm.State):
    """
    Base state class for tool states
    """
    def __init__(self, tool):
        self.tool = tool

    def enter(self):
        pass

    def leave(self):
        pass

    def update(self):
        pass

    def draw(self):
        pass


class Selection(object):
    """
    Handles grid based selections
    """
    def __init__(self, editor, **config):
        self.editor = editor
        self.start = None
        self.end = None
        self.color = config.get('color', SELECTION_DEFAULT_COLOR)
        self.input = self.editor.input
        self.visible = config.get('visible', True)
        self.mouse_up = False

    def update(self):
        """
        Obligatory update method
        """

        if self.input.button_pressed(LEFT_MOUSE_BUTTON):
            if not self.start or self.mouse_up:
                self.start = self.editor.selected
                self.mouse_up = False

            self.end = self.editor.selected

        if LEFT_MOUSE_BUTTON not in self.input.curr_button_state:
            self.mouse_up = True

    def draw(self):
        """
        Obligatory draw method
        """
        if not self.start or not self.visible:
            return

        width = abs(self.start[0] - self.end[0])
        height = abs(self.start[1] - self.end[1])

        left = min(self.start[0], self.end[0])
        top = min(self.start[1], self.end[1])

        r = pygame.Rect(
            left,
            top,
            width + constants.CELL_SIZE,
            height + constants.CELL_SIZE)

        pygame.draw.rect(self.editor.graphics.surf, self.color,  r, 1)

    def get_tiles(self):
        """
        Returns all selected tiles as a set (for faster lookup)
        """

        result = set()

        left = min(self.start[0], self.end[0])
        top = min(self.start[1], self.end[1])
        right = max(self.start[0], self.end[0])
        bottom = max(self.start[1], self.end[1])

        for row in range(top, bottom, constants.CELL_SIZE):
            for col in range(left, right, constants.CELL_SIZE):
                result.add((col, row))

        return result
