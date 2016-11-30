# -*- coding: utf-8 -*-
"""
Player module.
"""

from collections import deque

import pygame

from colors import WHITE, RED, ORANGE, BLUE
from snake import Snake, LEFT, RIGHT, UP, DOWN
from utils import add_vecs
from combat import Weapon, STD_MG, H_GUN, PLASMA_GUN, BOMB1_DROPPER
from settings import (INIT_BOOST, MAX_BOOST, BOOST_COST, BOOST_GAIN,
                      BOOST_SPEED, INIT_LIFES, MAX_LIFES, PORTAL_TAG,
                      PWRUP_TAG, SHOT_TAG, MAX_HITPOINTS)


class PlayerBase(object):

    """
    Player base class.
    """

    def __init__(self, g_mode, config):
        self.game = g_mode.game
        self.tilemap = g_mode.tilemap
        self.pid = config['id']
        self.color = config['color']
        self.snake_skin = config['skin']
        self.snake = None
        self._lifes = INIT_LIFES
        self.points = 0
        self._boost = INIT_BOOST
        self.boosting = False
        self.weapons = deque((
            Weapon(self.game, self, STD_MG),
            Weapon(self.game, self, H_GUN),
            Weapon(self.game, self, PLASMA_GUN),
            Weapon(self.game, self, BOMB1_DROPPER)))
        self.pwrup_targets = {'points': 'points', 'grow': 'snake.grow',
                              'speed': 'snake.speed', 'boost': 'boost',
                              'lifes': 'lifes', 'hp': 'snake.hitpoints'}

    def start(self):
        self.snake = Snake(self.game, self.tilemap.get_spawnpoint(),
                           self.snake_skin, self.pid, self.snake_killed)

    @property
    def lifes(self):
        """Return lifes."""
        return self._lifes

    @lifes.setter
    def lifes(self, value):
        """Set lifes."""
        if value > MAX_LIFES:
            self._lifes = MAX_LIFES
        elif value < 0:
            self._lifes = 0
        else:
            self._lifes = value

    @property
    def boost(self):
        """Return boost energy."""
        return self._boost

    @boost.setter
    def boost(self, value):
        """Set boost energy."""
        if value > MAX_BOOST:
            self._boost = MAX_BOOST
        elif value < 0:
            self._boost = 0
        else:
            self._boost = value

    def coll_check_head(self, collobjs):
        """Handle collisions for the snake's head."""
        for tag, obj in collobjs:
            if (tag.endswith('-body') or tag.endswith('-head')) and \
                    tag != self.snake.head_tag:
                obj.take_damage(35, self.snake.head_tag, False, True,
                                0.7, shrink=1, slowdown=0.03)
            elif tag == PORTAL_TAG:
                self.snake.heading = obj[1]
                self.snake[0] = add_vecs(obj[0], self.snake.heading)
            elif tag == PWRUP_TAG:
                for action in obj.actions:
                    target = self.pwrup_targets[action['target']]
                    if '.' in target:
                        target1, target2 = target.split('.')
                        attr = getattr(getattr(self, target1), target2)
                        setattr(getattr(self, target1),
                                target2, attr + action['value'])
                    else:
                        attr = getattr(self, target)
                        setattr(self, target, attr + action['value'])
                obj.collect()
            elif tag == SHOT_TAG:
                self.handle_shot(obj)

    def coll_check_body(self, collobjs):
        """Handle collisions for the snakes's body."""
        for tag, obj in collobjs:
            if tag == SHOT_TAG:
                self.handle_shot(obj)

    def handle_shot(self, shot):
        """Handle shot."""
        self.snake.take_damage(shot.damage, shot.tag, False, True, 1.2,
                               slowdown=shot.slowdown, shrink=1)
        shot.hit()

    def update(self, delta_time):
        """Update player, move snake."""
        if not self.snake:
            return

        self.snake.update(delta_time)

        self.weapons[0].update(delta_time)

        if self.snake.heading != self.snake.prev_heading:
            self.snake.ismoving = True

        if self.boost < BOOST_COST * delta_time:
            self.boosting = False
            self.snake.speed_bonus = 0

        if self.boosting:
            boost = self.boost - BOOST_COST * delta_time
            if boost < BOOST_COST * delta_time:
                self.boost = 0
            else:
                self.boost = boost
        else:
            self.boost = self.boost + BOOST_GAIN * delta_time

    def draw(self, offset):
        """Draw snake and UI."""
        if not self.snake:
            return

        self.snake.draw()

        gfx = self.game.graphics

        gfx.draw_string(add_vecs((2, 2), offset),
                        'Player{0}'.format(self.pid), self.color)

        gfx.draw_string(add_vecs((56, 2), offset),
                        '{0:.2f}'.format(self.snake.speed), WHITE)

        gfx.draw_string(add_vecs((2, 18), offset),
                        'Points: {0}'.format(self.points), WHITE)

        pygame.draw.rect(self.game.screen, ORANGE,
                         pygame.Rect(add_vecs((100, 2), offset),
                                     (104, 20)))

        # Draw life bar. TODO: Make this some kinda class.
        width = int(self.snake.hitpoints / float(MAX_HITPOINTS) * 100)
        rect = pygame.Rect(add_vecs((102, 4), offset), (width, 7))
        pygame.draw.rect(self.game.screen, RED, rect)

        width = int(self.boost / float(MAX_BOOST) * 100)
        rect = pygame.Rect(add_vecs((102, 13), offset), (width, 7))
        pygame.draw.rect(self.game.screen, BLUE, rect)

        gfx.draw_string(add_vecs((208, 2), offset),
                        '{0} {1}'.format(self.weapons[0].wtype,
                                         self.weapons[0].ammo), WHITE)

        for index in range(self.lifes):
            gfx.draw('life16x16', add_vecs((100, 24), offset),
                     gridcoords=False, offset=(index*18, 0))

    def snake_killed(self, killed_by):
        """Snake killed event handler."""
        if self.lifes > 0:
            self.lifes -= 1
            self.boost = MAX_BOOST
            self.snake.respawn(self.tilemap.get_spawnpoint())


class Player(PlayerBase):

    """
    Player class.
    """

    def __init__(self, g_mode, config):
        PlayerBase.__init__(self, g_mode, config)

        self.game.key_manager.key_down_event.append(self.key_down)
        self.game.key_manager.key_up_event.append(self.key_up)
        self.ctrls = config['ctrls']

    def key_down(self, key):
        """Key down event handler."""
        if key == self.ctrls['boost']:
            self.boosting = True
            self.snake.speed_bonus = BOOST_SPEED
        elif key == self.ctrls['action']:
            # Has the potential to cause an endless loop.
            while self.weapons[0].ammo <= 0:
                self.weapons.rotate(1)
            self.weapons[0].set_firing(True)

    def key_up(self, key):
        """Key up event handler."""
        if key == self.ctrls['boost']:
            self.boosting = False
            self.snake.speed_bonus = 0
        elif key == self.ctrls['action']:
            self.weapons[0].set_firing(False)

    def update(self, delta_time):
        """Update player."""

        PlayerBase.update(self, delta_time)

        if self.game.key_manager.key_pressed(self.ctrls['left']) \
                and self.snake.heading != RIGHT:
            self.snake.set_heading(LEFT)
        elif self.game.key_manager.key_pressed(self.ctrls['up']) \
                and self.snake.heading != DOWN:
            self.snake.set_heading(UP)
        elif self.game.key_manager.key_pressed(self.ctrls['down']) \
                and self.snake.heading != UP:
            self.snake.set_heading(DOWN)
        elif self.game.key_manager.key_pressed(self.ctrls['right']) \
                and self.snake.heading != LEFT:
            self.snake.set_heading(RIGHT)

        if self.game.key_manager.key_tapped(self.ctrls['nextweapon']):
            # Dangerous...
            self.weapons.rotate(1)
            while self.weapons[0].ammo <= 0:
                self.weapons.rotate(1)
