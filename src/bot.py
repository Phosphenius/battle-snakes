# -*- coding: utf-8 -*-

"""
Snake AI powered by a Finite State Machine and Potential Fields.
"""

from abc import abstractmethod
from heapq import nsmallest
from copy import copy

from player import PlayerBase
from fsm import State, StateMachine
from utils import m_distance, sub_vecs
from pathfinding import Pathfinder
from snake import get_next_to_portal


class BotState(State):

    """
    Base class for Bot States.
    """

    def __init__(self, bot):
        self.bot = bot

    @abstractmethod
    def update(self, delta_time):
        pass


class BotCollectState(BotState):

    """
    State class implementing the 'Collect State' in which the AI is attempting
    to collect powerups.
    """

    def __init__(self, bot):
        BotState.__init__(self, bot)
        self.prev_target = None
        self.target = None
        self.path = []
        self.pwrup_table = []

        self.snake = bot.snake
        self.game = bot.game

        self.t_alive = 0

    def update(self, delta_time):
        self.prev_target = self.target
        self.pwrup_table = []
        for pwrup in self.game.pwrup_manager.get_powerups():
            dis = m_distance(self.snake.body[0], pwrup.pos)
            score = self.bot.pwrup_score[pwrup.pid]

            self.pwrup_table.append((dis, score, pwrup))

        if not self.target:
            self.aquire_target()

        if self.target.pos not in \
                [elem[2].pos for elem in self.pwrup_table]:
            self.aquire_target()

        if self.prev_target != self.target:
            self.path = self.bot.pathfinder.find_path(self.snake[0],
                                                      self.target.pos)
            assert self.path

            self.path.insert(0, self.target.pos)
            heading = sub_vecs(self.path[-1], self.snake[0])
            self.bot.snake.set_heading(heading)

        if self.path[-1] == self.snake[0] and len(self.path) >= 1:
            if m_distance(self.path[-1], self.path[-2]) > 1:
                portal = get_next_to_portal(self.snake[0],
                                            self.game.tilemap)
                if portal:
                    heading = sub_vecs(portal, self.snake[0])
                else:
                    heading = sub_vecs(self.snake[0], self.path[-2])

            else:
                heading = sub_vecs(self.path[-2], self.snake[0])
            self.path.pop()
            self.bot.snake.set_heading(heading)

    def enter(self, old_state):
        pass

    def leave(self):
        pass

    def aquire_target(self):
        selection = nsmallest(4, self.pwrup_table)
        self.target = copy(self.game.randomizer.choice(selection)[2])


class BotAttackState(BotState):

    """
    Not implemented yet.
    """

    def __init__(self, bot):
        BotState.__init__(self, bot)

    def update(self, delta_time):
        pass

    def enter(self, old_state):
        pass

    def leave(self):
        pass


class Bot(PlayerBase, StateMachine):

    """
    Basic bot class.
    """

    def __init__(self, game_mode, dead_handler, kwargs):
        PlayerBase.__init__(self, game_mode, dead_handler, **kwargs)
        StateMachine.__init__(self, BotCollectState(self))

        self.pathfinder = Pathfinder(self.game)
        self.pwrup_target_weights = {'points': -0.1, 'grow': 0.1,
                                     'speed': -0.05, 'boost': -0.00001,
                                     'lifes': -100, 'hp': -0.8}
        self.pwrup_score = {}

        for pwrup in list(self.game.pwrup_manager.pwrup_prototypes.values()):
            pid = pwrup['pid']
            self.pwrup_score[pid] = 0
            targets = pwrup['actions']
            num_targets = len(targets)

            for target in targets:
                weight = self.pwrup_target_weights[target['target']]
                self.pwrup_score[pid] += target['value'] * weight
            self.pwrup_score[pid] *= num_targets

    def update(self, delta_time):
        """Update fsm and player base."""

        self.current_state.update(delta_time)
        PlayerBase.update(self, delta_time)
