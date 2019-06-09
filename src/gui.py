# -*- coding: utf-8 -*-

"""
Collection of widgets and containers to make up a keyboard-only GUI.
All widgets have to be placed inside a container.
"""

import textwrap
from collections import deque

import pygame
from pygame.locals import K_UP, K_DOWN, K_RETURN, K_LEFT, K_RIGHT

from utils import add_vecs
from constants import (GRAY, RED, YELLOW, BLACK, WHITE, GREEN, 
                    DARK_PURPLE, ORANGE, WIDGET_HEIGHT,
                    WIDGET_BG_COLOR, WIDGET_BORDER_THICKNESS,
                    WIDGET_BORDER_COLOR, WIDGET_BORDER_FOCUS_COLOR,
                    WIDGET_DISABLED_BORDER_COLOR, TEXT_WIDGET_TEXT_COLOR,
                    TEXT_WIDGET_TEXT_COLOR_FOCUS,
                    TEXT_WIDGET_DISABLED_TEXT_COLOR, LABEL_WIDGET_TEXT_COLOR,
                    LABEL_WIDGET_BORDER_COLOR, TRIANGLE_WIDTH,
                    STACK_PANEL_PAD_Y)


def label(game, **kwargs):
    config = {}

    if 'text_color' not in kwargs:
        config['text_color'] = LABEL_WIDGET_TEXT_COLOR

    if 'brd_color' not in kwargs:
        config['brd_color'] = LABEL_WIDGET_BORDER_COLOR

    if 'focus_enabled' not in kwargs:
        config['focus_enabled'] = False

    kwargs.update(config)

    return TextWidget(game, **kwargs)


class StandaloneContainer(object):
    """Container that allows to place a single widget at absolute
    coordinates with defined dimensions."""
    def __init__(self, game, pos, width, height, widget, focus=False):
        self.game = game
        self.pos = pos
        self.width = width
        self.widget = widget
        self.widget.height = height

        if self.widget.focus_enabled:
            self.widget.focus = focus

    def update(self, delta_time):
        self.widget.update(delta_time)

    def draw(self):
        self.widget.draw(self.pos, self.width)


class StackPanel(object):
    """Simple container that stacks widgets vertically."""
    def __init__(self, game, pos, width, **kwargs):
        self.game = game
        self.pos = pos
        self.width = width
        self.pady = kwargs.get('pady', STACK_PANEL_PAD_Y)
        self.action_keys = kwargs.get('action_keys', (K_UP, K_DOWN))
        self.widgets = list()
        self.selected = 0

        self.focusable_widgets = False

        self.action = kwargs.get('action', None)

    def add_widgets(self, *args):
        self.widgets.extend(args)

        for index in range(len(self.widgets)):
            if (self.widgets[index].enabled and
                    self.widgets[index].focus_enabled):
                self.selected = index
                self.widgets[self.selected].focus = True
                self.focusable_widgets = True
                break

    def change_focus(self, index):
        # TODO: Add some checks
        self.widgets[self.selected].focus = False
        self.selected = index
        self.widgets[self.selected].focus = True

    def update(self, delta_time):

        for widget in self.widgets:
            widget.update(delta_time)

        if None in self.action_keys:
            return

        # TODO: Check if the currently focused widget still has focus.

        if (self.game.key_manager.key_tapped(self.action_keys[0]) and
                self.focusable_widgets):
            self.widgets[self.selected].focus = False

            while True:
                self.selected -= 1

                if self.selected < 0:
                    self.selected = len(self.widgets) - 1

                if (self.widgets[self.selected].enabled and
                        self.widgets[self.selected].focus_enabled):
                    break

            self.widgets[self.selected].focus = True
            self.on_action()
        elif (self.game.key_manager.key_tapped(self.action_keys[1]) and
              self.focusable_widgets):
            self.widgets[self.selected].focus = False

            while True:
                self.selected += 1

                if self.selected > (len(self.widgets) - 1):
                    self.selected = 0

                if (self.widgets[self.selected].enabled and
                        self.widgets[self.selected].focus_enabled):
                    break

            self.widgets[self.selected].focus = True
            self.on_action()

    def on_action(self):
        if self.action:
            self.action(self.selected)

    def draw(self):
        xpos, ypos = self.pos

        for widget in self.widgets:
            widget.draw((xpos, ypos), self.width)

            ypos += widget.height + self.pady


class WidgetBase(object):
    """Base class for widgets."""
    def __init__(self, game, **kwargs):
        self.game = game
        self.height = kwargs.get('height', WIDGET_HEIGHT)
        self.bg_color = kwargs.get('bg_color', WIDGET_BG_COLOR)
        self.brd_thickness = kwargs.get('brd_thickness',
                                        WIDGET_BORDER_THICKNESS)
        self.brd_color = kwargs.get('brd_color',
                                    WIDGET_BORDER_COLOR)
        self.enabled = kwargs.get('enabled', True)
        self.focus_color = kwargs.get('focus_color',
                                      WIDGET_BORDER_FOCUS_COLOR)
        self.focus_enabled = kwargs.get('focus_enabled', True)
        self.big_text = kwargs.get('big_text', True)

        self._focus = False
        self.brd_color_no_focus = self.brd_color

    @property
    def focus(self):
        return self._focus

    @focus.setter
    def focus(self, focus):
        if self.focus_enabled:
            self._focus = focus

            if self._focus:
                self.brd_color = self.focus_color
            else:
                self.brd_color = self.brd_color_no_focus

    def update(self, delta_time):
        pass

    def draw(self, pos, width):
        border_color = self.brd_color

        if not self.enabled:
            border_color = WIDGET_DISABLED_BORDER_COLOR

        # Draw border
        border = pygame.Rect(pos, (width, self.height))
        pygame.draw.rect(self.game.screen, border_color, border)

        # Draw background
        bg_size = (border.width - self.brd_thickness * 2,
                   border.height - self.brd_thickness * 2)
        bg_pos = add_vecs(pos,
                         (self.brd_thickness, self.brd_thickness))
        background = pygame.Rect(bg_pos, bg_size)
        pygame.draw.rect(self.game.screen, self.bg_color, background)


class TextWidget(WidgetBase):
    """A widget which displays a single line of text."""
    def __init__(self, game, **kwargs):
        WidgetBase.__init__(self, game, **kwargs)
        self.text = kwargs.get('text', '')
        self.text_color = kwargs.get('text_color',
                                     TEXT_WIDGET_TEXT_COLOR)
        self.text_color_focus = kwargs.get('text_color_focus',
                                           TEXT_WIDGET_TEXT_COLOR_FOCUS)

    def draw(self, pos, width):
        WidgetBase.draw(self, pos, width)

        text_color = self.text_color

        if not self.enabled:
            text_color = TEXT_WIDGET_DISABLED_TEXT_COLOR
        elif self.focus_enabled and self.focus:
            text_color = self.text_color_focus

        size = self.game.graphics.get_size(self.text, big=self.big_text)

        center = (width / 2 - size[0] / 2,
                  self.height / 2 - size[1] / 2)
        self.game.graphics.draw_string(add_vecs(center, pos),
                                       self.text,
                                       text_color,
                                       big=self.big_text)


class Button(TextWidget):
    """A Button widget."""
    def __init__(self, game, **kwargs):
        self.action = kwargs.get('action', None)
        self.action_key = kwargs.get('action_key', K_RETURN)

        TextWidget.__init__(self, game, **kwargs)

    def on_action(self):
        if self.action:
            self.action()

    def update(self, delta_time):
        TextWidget.update(self, delta_time)

        if not self.action_key:
            return

        if self.game.key_manager.key_tapped(self.action_key) and self.focus:
            self.on_action()


class CycleButton(TextWidget):
    def __init__(self, game, **kwargs):
        TextWidget.__init__(self, game, **kwargs)
        self.elements = deque(kwargs.get('elements', ['empty']))
        self.action = kwargs.get('action', None)
        self.action_keys = kwargs.get('action_keys', (K_LEFT, K_RIGHT))
        self.hl_right_t = 0
        self.hl_left_t = 0

    def on_action(self):
        if self.action:
            self.action(self.elements[0])

    def update(self, delta_time):
        TextWidget.update(self, delta_time)

        if self.focus:

            if self.hl_right_t > 0:
                self.hl_right_t -= delta_time

            if self.hl_left_t > 0:
                self.hl_left_t -= delta_time

            if None in self.action_keys:
                return

            if self.game.key_manager.key_tapped(self.action_keys[1]):
                self.elements.rotate(-1)
                self.hl_right_t = 0.035
                self.on_action()
            elif self.game.key_manager.key_tapped(self.action_keys[0]):
                self.elements.rotate(1)
                self.hl_left_t = 0.035
                self.on_action()

    def _draw_triangle(self, pos, highlight, face_right=False):
        xpos, ypos = pos
        xpos += self.brd_thickness * 2 + TRIANGLE_WIDTH
        ypos += self.brd_thickness * 2
        height = self.height - (self.brd_thickness * 4)

        color = BLACK
        triangle_wi = TRIANGLE_WIDTH

        if not self.big_text:
            triangle_wi -= 10

        if highlight:
            color = GREEN

        if face_right:
            lines = [(xpos - triangle_wi, ypos),
                     (xpos - triangle_wi, ypos + height),
                     (xpos, ypos + height / 2)]
        else:
            lines = [(xpos, ypos),
                     (xpos, ypos + height),
                     (xpos - triangle_wi, ypos + height / 2)]

        pygame.draw.aalines(self.game.screen, color, True, lines, True)

    def draw(self, pos, width):
        self.text = self.elements[0]

        TextWidget.draw(self, pos, width)

        if self.big_text:
            self._draw_triangle(pos, self.hl_left_t > 0)
        else:
            self._draw_triangle((pos[0]-10, pos[1]), self.hl_left_t > 0)

        tri_x = pos[0] + width - TRIANGLE_WIDTH - self.brd_thickness * 4

        self._draw_triangle((tri_x, pos[1]),
                            self.hl_right_t > 0,
                            True)


class TextDisplay(WidgetBase):
    """A multi line textbox widget which automatically wraps text."""
    def __init__(self, game, **kwargs):
        WidgetBase.__init__(self, game, **kwargs)
        self.text = kwargs.get('text', '')

    def set_text(self, text):
        self.text = text

    def draw(self, pos, width):
        WidgetBase.draw(self, pos, width)

        num_chars = width / self.game.graphics.get_size('a')[0]

        xpos, ypos = add_vecs(pos,
                              (self.brd_thickness, self.brd_thickness))
        for line in textwrap.wrap(self.text, width=num_chars):
            self.game.graphics.draw_string((xpos, ypos), line, WHITE)
            ypos += self.game.graphics.get_height()


class SnakeAvatar(WidgetBase):
    def __init__(self, game, skin, **kwargs):
        WidgetBase.__init__(self, game, **kwargs)

        self.focus_enabled = False
        self.height = 50
        self.skin = skin

        self.fake_snake = (((00, 00), pygame.Rect(00, 10, 10, 10)),
                           ((10, 00), pygame.Rect(30, 30, 10, 10)),
                           ((20, 00), pygame.Rect(20, 30, 10, 10)),
                           ((30, 00), pygame.Rect(10, 20, 10, 10)),
                           ((30, 10), pygame.Rect(00, 30, 10, 10)),
                           ((40, 10), pygame.Rect(30, 30, 10, 10)),
                           ((50, 10), pygame.Rect(20, 30, 10, 10)),
                           ((60, 10), pygame.Rect(30, 30, 10, 10)),
                           ((70, 10), pygame.Rect(20, 10, 10, 10)))

    def update(self, delta_time):
        WidgetBase.update(self, delta_time)

    def draw(self, pos, width):
        WidgetBase.draw(self, pos, width)

        offset = (self.brd_thickness, self.brd_thickness)
        offset = add_vecs(offset, (100, 10))

        for snake_pos, skin_area in self.fake_snake:
            self.game.graphics.draw(self.skin, add_vecs(snake_pos, pos),
                                    gridcoords=False, area=skin_area,
                                    offset=offset)


class PlayerSlot(object):
    def __init__(self, game, pos, **kwargs):
        self.game = game
        self.stack_panel = StackPanel(game, pos, 300, pady=2,
                                      action_keys=(None, None))

        self.num_weapons = kwargs.get('weapons', 0)
        self._player = False
        self._ready = False

        # TODO: Color this according to player id
        self.lbl_playerid = label(game, text='<open>',
                                  height=30, big_text=False,
                                  focus_enabled=True, focus=True,
                                  brd_color=ORANGE)

        self.lbl_skin = label(game, text='Skin:', height=30,
                              big_text=False)

        self.skin_full_names = {}
        skins = []

        for skin in self.game.graphics.get_startswith('skin'):
            shortened = skin[5:]
            self.skin_full_names[shortened] = skin
            skins.append(shortened)

        self.cyc_skin = CycleButton(game, height=30, big_text=False,
                                    elements=skins,
                                    action=self.cyc_skin_action,
                                    action_keys=(None, None))

        init_skin = self.skin_full_names[self.cyc_skin.elements[0]]
        self.snake_av = SnakeAvatar(game, init_skin)

        self.stack_panel.add_widgets(self.lbl_playerid, self.snake_av,
                                     self.lbl_skin, self.cyc_skin)

        # TODO: Put widgets into list so we can access outside init.
        for index in range(self.num_weapons):
            lab = label(game, text='Weapon{0}:'.format(index),
                        height=30, big_text=False)
            cyc_btn = CycleButton(game, height=30, big_text=False,
                                  action_keys=(None, None))

            self.stack_panel.add_widgets(lab, cyc_btn)

        self.btn_ready = Button(game, text='Ready', height=30,
                                big_text=False,
                                action_key=None,
                                action=self.btn_ready_action)
        self.btn_abort = Button(game, text='Abort', height=30,
                                big_text=False,
                                action_key=None,
                                action=self.btn_abort_action)

        self.stack_panel.add_widgets(self.btn_ready, self.btn_abort)

    def btn_ready_action(self):
        self._ready = True

        self.btn_ready.enabled = False
        self.cyc_skin.enabled = False

    def btn_abort_action(self):
        self._ready = False
        self.btn_ready.enabled = True
        self.cyc_skin.enabled = True

    def get_ready(self):
        return self._ready

    def is_empty(self):
        return not self._player

    @property
    def player(self):
        return self._player

    @player.setter
    def player(self, player):
        self._player = player

        skin = self.skin_full_names[self.cyc_skin.elements[0]]
        self._player['skin'] = skin

        self.stack_panel.action_keys = (player['ctrls']['up'],
                                        player['ctrls']['down'])

        self.cyc_skin.action_keys = (player['ctrls']['left'],
                                     player['ctrls']['right'])

        for btn in (self.btn_abort, self.btn_ready):
            btn.action_key = player['ctrls']['action']

        self.lbl_playerid.text = 'Player{0}'.format(player['id'])
        self.lbl_playerid.text_color = player['color']
        self.lbl_playerid.focus = False
        self.lbl_playerid.focus_enabled = False
        self.stack_panel.change_focus(3)

    def cyc_skin_action(self, new_val):
        self.snake_av.skin = self.skin_full_names[new_val]
        self._player['skin'] = self.skin_full_names[new_val]

    def update(self, delta_time):
        self.stack_panel.update(delta_time)

    def draw(self):
        self.stack_panel.draw()
