# -*- coding: utf-8 -*-
"""
Player module.
"""

from collections import deque

import pygame
from pygame.locals import (K_LEFT, K_RIGHT, K_UP, K_DOWN, K_l, K_k, K_j,
                           K_a, K_d, K_w, K_s, K_c, K_v, K_b)

from colors import WHITE, RED, ORANGE, BLUE
from snake import Snake, LEFT, RIGHT, UP, DOWN
from utils import add_vecs
from combat import Weapon, STD_MG, H_GUN, PLASMA_GUN
from settings import (INIT_BOOST, MAX_BOOST, BOOST_COST, BOOST_GAIN,
                      BOOST_SPEED, INIT_LIFES, MAX_LIFES, PORTAL_TAG,
                      PWRUP_TAG, SHOT_TAG, MAX_HITPOINTS)

# -- Controls --
CTRLS1 = {'left': K_LEFT, 'right': K_RIGHT, 'up': K_UP, 'down': K_DOWN,
          'action': K_l, 'boost': K_k, 'nextweapon': K_j}

CTRLS2 = {'left': K_a, 'right': K_d, 'up': K_w, 'down': K_s, 'action': K_c,
          'boost': K_v, 'nextweapon': K_b}

# -- Players --
PLAYER1 = {'id': '1', 'color': BLUE, 'ctrls': CTRLS1,
           'tex': 'snake_body_p1'}

PLAYER2 = {'id': '2', 'color': RED, 'ctrls': CTRLS2,
           'tex': 'snake_body_p2'}

BOT = {'id': 2, 'color': RED, 'tex': 'snake_body_p2'}


class PlayerBase(object):

    """
    Player base class.
    """

    def __init__(self, game, config):
        self.game = game
        self.pid = config['id']
        self.color = config['color']
        self.snake = Snake(game, game.get_spawnpoint(),
                           config['tex'], self.pid, self.snake_killed)
        self._lifes = INIT_LIFES
        self.points = 0
        self._boost = INIT_BOOST
        self.boosting = False
        self.weapons = deque((
            Weapon(self.game, self, STD_MG),
            Weapon(self.game, self, H_GUN),
            Weapon(self.game, self, PLASMA_GUN)))
        self.pwrup_targets = {'points': 'points', 'grow': 'snake.grow',
                              'speed': 'snake.speed', 'boost': 'boost',
                              'lifes': 'lifes', 'hp': 'snake.hitpoints'}

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
        self.snake.draw()
        self.game.draw_string('Player{0}'.format(self.pid),
                              add_vecs((2, 2), offset), self.color)
        self.game.draw_string('{0:.2f}'.format(self.snake.speed),
                              add_vecs((56, 2), offset), WHITE)
        self.game.draw_string('Points: {0}'.format(self.points),
                              add_vecs((2, 18), offset), WHITE)

        pygame.draw.rect(self.game.screen, ORANGE,
                         pygame.Rect(add_vecs((100, 2), offset), (104, 20)))

        pygame.draw.rect(self.game.screen, RED,
                         pygame.Rect(add_vecs((102, 4), offset), (int(
                             self.snake.hitpoints /
                             float(MAX_HITPOINTS) * 100), 7)))

        pygame.draw.rect(self.game.screen, BLUE,
                         pygame.Rect(add_vecs((102, 13), offset), (int(
                             self.boost / float(MAX_BOOST) * 100), 7)))

        self.game.draw_string('{0} {1}'.format(self.weapons[0].wtype,
                                               self.weapons[0].ammo),
                              add_vecs((208, 2), offset), WHITE)

        for i in range(self.lifes):
            self.game.graphics.draw('life16x16', add_vecs((100, 24), offset),
                                    gridcoords=False, offset=(i*18, 0))

    def snake_killed(self, killed_by):
        """Snake killed event handler."""
        if self.lifes > 0:
            self.lifes -= 1
            self.boost = MAX_BOOST
            self.snake.respawn(self.game.get_spawnpoint())


class Player(PlayerBase):

    """
    Player class.
    """

    def __init__(self, game, config):
        PlayerBase.__init__(self, game, config)

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
