#!/usr/bin/python
# -*- coding: utf-8 -*-

'''Main module of the game'''

import sys
import glob
import os
import random
from collections import defaultdict

import pygame
from pygame.locals import QUIT, K_q, K_ESCAPE

from colors import WHITE, BLACK
from utils import add_vecs, mul_vec
from powerup import PowerupManager
from player import Player, PLAYER1, BOT
from bot import Bot
from combat import ShotManager
from map import Map
from settings import (PANEL_H, CELL_SIZE, SCR_W, SCR_H, SPAWNPOINT_TAG,
                      PORTAL_TAG, PWRUP_TAG, SHOT_TAG, WALL_TAG)

VERSION = 'v0.2.1'


def quit_game():
    """Quit the game."""
    pygame.quit()
    sys.exit()


class GraphicsManager(object):
    '''Simple graphics manager'''
    def __init__(self, surf):
        self.surf = surf
        self.textures = {}
        for img in glob.glob('../gfx/*.png'):
            surf = pygame.image.load(img)

            if surf.get_alpha() is None:
                surf = surf.convert()
            else:
                surf = surf.convert_alpha()

            self.textures[os.path.splitext(os.path.split(img)[1])[0]] = surf

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
        '''Determine if any of the keys passed as an argument is pressed.'''
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


class BattleSnakesGame(object):

    """
    Main class representing the game.
    """

    def __init__(self, res):
        pygame.init()
        pygame.display.set_caption("Battle Snakes {0}".format(VERSION))

        self.randomizer = random.Random(11)
        self.sysfont = pygame.font.SysFont('Arial', 14)
        self.screen = pygame.display.set_mode(res)
        self.fps_clock = pygame.time.Clock()
        self.key_manager = KeyManager()
        self.graphics = GraphicsManager(self.screen)
        self.pwrup_manager = PowerupManager(self)
        self.shot_manager = ShotManager(self)
        self.tilemap = Map(self, '../data/maps/map02.xml')

        self.spatialhash = defaultdict(list)

        self.players = []
        self.build_sh()
        self.players.append(Player(self, PLAYER1))
        self.build_sh()
        self.players.append(Bot(self, BOT))

        self.pwrup_manager.spawn_pwrup('food1',
                                       int(len(self.players)*5))

        self.pwrup_manager.spawn_pwrup('food2',
                                       int(len(self.players)*2.5))

        self.pwrup_manager.spawn_pwrup('food3', len(self.players))

        self.pwrup_manager.autospawn('evilthing', 12)
        self.pwrup_manager.autospawn('speedup1', 2)
        self.pwrup_manager.autospawn('heal', 1.2)
        self.pwrup_manager.autospawn('jackpot', 1, 60)
        self.pwrup_manager.autospawn('life', 0.75, 120)

    def toroidal(self, obj):
        """Treats 'obj' as if the play field was toroidal."""
        xpos, ypos = obj
        if xpos < 0:
            obj = (self.tilemap.width-1, ypos)
        if xpos > self.tilemap.width-1:
            obj = (0, ypos)
        if ypos < 0:
            obj = (xpos, self.tilemap.height-1)
        if ypos > self.tilemap.height-1:
            obj = (xpos, 0)
        return obj

    def get_spawnpoint(self):
        """Return  random, unblocked spawnpoint."""
        return self.randomizer.choice([spawnpoint for spawnpoint in
                                       self.tilemap.spawnpoints
                                       if self.sp_unblocked(spawnpoint)])

    def randpos(self):
        """Return random position."""
        while True:
            pos = (self.randomizer.randint(1, self.tilemap.width-1),
                   self.randomizer.randint(1, self.tilemap.height-1))
            if pos not in self.spatialhash and pos not in self.tilemap.tiles:
                return pos

    def isunblocked(self, pos):
        """Test if a cell is blocked by something."""
        return len(self.spatialhash.get(pos, [])) == 0

    def in_bounds(self, pos):
        """Determine if pos is in bounds of the map."""
        # I think, this methods belongs to the map class...
        return pos[0] >= 0 and pos[0] <= self.tilemap.width and \
            pos[1] >= 0 and pos[1] <= self.tilemap.height

    def sp_unblocked(self, spawnpoint):
        """Determine if a spawnpoint is blocked."""
        return len(self.spatialhash[spawnpoint]) == 1

    def build_sh(self):
        """Build spatial hash."""
        self.spatialhash.clear()

        # Add spawnpoints (So powerups don't appear on them)
        for spawnpoint in self.tilemap.spawnpoints:
            self.spatialhash[spawnpoint].append((SPAWNPOINT_TAG,
                                                 spawnpoint))

        # Add portals
        for portal_key, portal_val in self.tilemap.portals.items():
            self.spatialhash[portal_key].append((PORTAL_TAG, portal_val))

        # Add powerups
        for pwrup in self.pwrup_manager.pwrup_pool:
            if pwrup.isalive:
                self.spatialhash[pwrup.pos].append((PWRUP_TAG, pwrup))

        # Add shots
        for shot in self.shot_manager.shot_pool:
            if shot.isalive:
                self.spatialhash[shot.pos].append((SHOT_TAG, shot))

        # Add snakes
        for player in self.players:
            self.spatialhash[player.snake[0]].append((
                player.snake.head_tag, player.snake))
            for snake in player.snake[1:]:
                self.spatialhash[snake].append((player.snake.body_tag,
                                                player.snake))

    def update(self, delta_time):
        """Update the game."""
        self.key_manager.update()

        self.pwrup_manager.update(delta_time)
        self.shot_manager.update(delta_time)

        for player in self.players:
            player.update(delta_time)

        self.build_sh()

        if self.key_manager.any_pressed(K_q, K_ESCAPE):
            quit_game()

        self.handle_collisions()

    def handle_collisions(self):
        """Handle collisions."""
        for player in self.players:
            if player.snake[0] in self.tilemap.tiles:
                player.snake.take_damage(20, WALL_TAG, True, True, 1,
                                         shrink=0, slowdown=0.07)
                break

        for shot in self.shot_manager.shot_pool:
            if shot.pos in self.tilemap.tiles:
                shot.hit()
            if shot.pos in self.tilemap.portals:
                shot.heading = self.tilemap.portals[shot.pos][1]
                shot.pos = add_vecs(self.tilemap.portals[shot.pos][0],
                                    shot.heading)

        for entries in self.spatialhash.values():
            if len(entries) > 1:
                for player in self.players:
                    for entry in entries:
                        if entry[0] == player.snake.head_tag:
                            player.coll_check_head(entries)
                        if entry[0] == player.snake.body_tag:
                            player.coll_check_body(entries)

    def draw(self):
        """Render."""
        self.tilemap.draw()

        self.pwrup_manager.draw()
        self.shot_manager.draw()

        pygame.draw.rect(self.screen, (32, 32, 32),
                         pygame.Rect(0, 0, SCR_W, PANEL_H))

        for i, player in enumerate(self.players):
            player.draw(mul_vec((290, 0), i))

        self.draw_string('FPS: {0:.2f}'.
                         format(self.fps_clock.get_fps()), (1200, 2), WHITE)

    def draw_string(self, text, pos, color):
        """Draw string."""
        self.screen.blit(self.sysfont.render(text, True, color), pos)

    def Run(self):
        """Run the game(Game loop)."""
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    quit_game()
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
