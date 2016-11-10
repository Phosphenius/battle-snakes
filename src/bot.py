# -*- coding: utf-8 -*-

"""
Snake AI powered by a Finite State Machine and Potential Fields.
"""

from abc import abstractmethod
from heapq import nsmallest
from copy import copy

from player import PlayerBase
from fsm import State, FiniteStateMachine
from utils import m_distance, sub_vecs
from astar import AStar


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
            self.path.insert(0, self.target.pos)
            heading = sub_vecs(self.path[-1], self.snake[0])
            self.bot.snake.set_heading(heading)

        if len(self.path) >= 1:
            if self.path[-1] == self.snake[0]:
                self.path.pop()

                heading = sub_vecs(self.path[-1], self.snake[0])
                self.bot.snake.set_heading(heading)

    def enter(self):
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

    def enter(self):
        pass

    def leave(self):
        pass


class Bot(PlayerBase, FiniteStateMachine):

    """
    Basic bot class.
    """

    def __init__(self, game, config):
        PlayerBase.__init__(self, game, config)
        FiniteStateMachine.__init__(self, BotCollectState(self))

        self.pathfinder = AStar(self.game.tilemap.width,
                                self.game.tilemap.height,
                                self.game.tilemap.tiles)
        self.pwrup_target_weights = {'points': -0.1, 'grow': 0.1,
                                     'speed': -0.05, 'boost': -0.00001,
                                     'lifes': -100, 'hp': -0.8}
        self.pwrup_score = {}

        for pwrup in self.game.pwrup_manager.pwrup_prototypes.values():
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

        self.curr_state.update(delta_time)
        PlayerBase.update(self, delta_time)
