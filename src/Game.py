#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Main module of the game"""

import sys
import glob
import os
import random
from ConfigParser import SafeConfigParser

import pygame
from pygame.locals import QUIT

from gsm import MenuState
from fsm import FiniteStateMachine
from colors import WHITE, BLACK
from utils import add_vecs, mul_vec
from constants import PANEL_H, CELL_SIZE, SCR_W, SCR_H
from combat import ShotManager

NUM_HUMAN_PLAYERS = 2

VERSION = 'v0.2.1'


class GraphicsManager(object):
    """Simple graphics manager"""
    def __init__(self, surf):
        self.surf = surf
        self.textures = {}
        for img in glob.glob('../gfx/*.png'):
            surf = pygame.image.load(img)

            if surf.get_alpha() is None:
                surf = surf.convert()
            else:
                surf = surf.convert_alpha()

            name = os.path.splitext(os.path.split(img)[1])[0]
            self.textures[name] = surf

        font_path = '../fonts/Xolonium-Regular.ttf'
        self.xolonium_font14 = pygame.font.Font(font_path, 14)
        self.xolonium_font20 = pygame.font.Font(font_path, 20)

    def draw(self, tex_name, pos, gridcoords=True, offset=(0, PANEL_H),
             area=None):
        """Draw a texture."""
        if tex_name not in self.textures:
            raise Exception('No such texture: {0}'.format(tex_name))
        if gridcoords:
            self.surf.blit(self.textures[tex_name],
                           add_vecs(mul_vec(pos, CELL_SIZE), offset),
                           area=area)
        else:
            self.surf.blit(self.textures[tex_name],
                           add_vecs(pos, offset), area=area)

    def draw_string(self, pos, text, color, big=False):
        if big:
            font_surf = self.xolonium_font20.render(text, True, color)
        else:
            font_surf = self.xolonium_font14.render(text, True, color)
        self.surf.blit(font_surf, pos)

    def get_size(self, text, big=False):
        if big:
            return self.xolonium_font20.size(text)
        else:
            return self.xolonium_font14.size(text)

    def get_height(self, big=False):
        if big:
            return self.xolonium_font20.get_height()
        else:
            return self.xolonium_font14.get_height()

    def get_startswith(self, startswith):
        # TODO: Maybe refactor?
        result = []

        for key in self.textures.keys():
            if key.startswith(startswith):
                result.append(key)

        return result


class KeyManager(object):

    """Simple input manager"""

    def __init__(self):
        self.curr_key_state = pygame.key.get_pressed()
        self.prev_key_state = None
        self.any_key_pressed = False
        self.key_down_event = []
        self.key_up_event = []

    def update(self):
        """Update the key manager"""
        self.prev_key_state = self.curr_key_state
        self.curr_key_state = pygame.key.get_pressed()
        self.any_key_pressed = any(self.curr_key_state)

        for k in range(len(self.curr_key_state)):
            if self.curr_key_state[k] and not self.prev_key_state[k]:
                self.on_key_down(k)
            elif not self.curr_key_state[k] and self.prev_key_state[k]:
                self.on_key_up(k)

    def key_pressed(self, key):
        """Test if the specified key is pressed."""
        return self.curr_key_state[key]

    def key_tapped(self, key):
        """Test if the specified key has been tapped."""
        return not self.curr_key_state[key] and self.prev_key_state[key]

    def any_pressed(self, *keys):
        """
        Determine if any of the keys passed as an argument is pressed.
        """
        return any([self.curr_key_state[k] for k in keys])

    def any_tapped(self, *keys):
        """Test if any of the specified keys was been tapped."""
        return any([not self.curr_key_state[k] and
                    self.prev_key_state[k] for k in keys])

    def on_key_up(self, key):
        """Invoke key up event."""
        for event in self.key_up_event:
            if event is not None:
                event(key)

    def on_key_down(self, key):
        """Invoke key down event."""
        for event in self.key_down_event:
            if event is not None:
                event(key)


def load_player_config(hpid):
    config_parser = SafeConfigParser()
    config = {'hpid': hpid, 'ctrls': {}}

    # TODO: Make path platform independent
    config_parser.read('../data/player_{0}.cfg'.format(hpid))

    config['ctrls']['left'] = config_parser.getint('controls', 'left')
    config['ctrls']['right'] = config_parser.getint('controls', 'right')
    config['ctrls']['up'] = config_parser.getint('controls', 'up')
    config['ctrls']['down'] = config_parser.getint('controls', 'down')
    config['ctrls']['action'] = config_parser.getint('controls',
                                                     'action')
    config['ctrls']['boost'] = config_parser.getint('controls', 'boost')
    config['ctrls']['nextweapon'] = config_parser.getint('controls',
                                                'nextweapon')
    return config


class BattleSnakesGame(FiniteStateMachine):

    """
    Main class representing the game.
    """

    def __init__(self, res):
        pygame.init()
        pygame.display.set_caption("Battle Snakes {0}".format(VERSION))

        self.randomizer = random.Random(13)
        self.screen = pygame.display.set_mode(res)
        self.fps_clock = pygame.time.Clock()
        self.key_manager = KeyManager()
        self.graphics = GraphicsManager(self.screen)

        self.shot_manager = ShotManager(self)

        self.h_player_configs = []

        for hpid in range(NUM_HUMAN_PLAYERS):
            self.h_player_configs.append(load_player_config(hpid))

        FiniteStateMachine.__init__(self, MenuState(self))

    def update(self, delta_time):
        """Update the game."""
        self.key_manager.update()
        self.curr_state.update(delta_time)

    def draw(self):
        """Render."""
        self.curr_state.draw()
        fps_string = 'FPS: {0:.2f}'.format(self.fps_clock.get_fps())
        self.graphics.draw_string((1200, 2), fps_string, WHITE)

    def quit(self):
        """Quit the game."""
        pygame.quit()
        sys.exit()

    def Run(self):
        """Run the game(Game loop)."""
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.quit()
            self.screen.fill(BLACK)
            delta_time = (self.fps_clock.tick(60) / 1000.0)
            self.update(delta_time)
            self.draw()
            pygame.display.update()


def main():
    """Create game object."""
    game = BattleSnakesGame((SCR_W, SCR_H))
    game.Run()

if __name__ == '__main__':
    main()
