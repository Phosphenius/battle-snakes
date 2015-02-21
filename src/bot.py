# -*- coding: utf-8 -*-

"""
Snake AI powered by a Finite State Machine and Potential Fields.
"""

from abc import abstractmethod
from copy import copy

from player import PlayerBase
from fsm import State, FiniteStateMachine
from utils import sub_vecs, m_distance


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
    to collect powerups. This is done by using Potential Fields which
    attract the AI the particular powerup.
    """

    def __init__(self, bot):
        BotState.__init__(self, bot)

        self.no_pwrups = True
        self.pot_field = None
        self.next_tile = self.bot.snake[0]
        self.target_pwrup = None
        self.map_width = self.bot.game.tilemap.width
        self.map_height = self.bot.game.tilemap.height

    def compute_pot_field(self):
        # Get nearest powerup.
        self.target_pwrup = copy(min([(m_distance(self.bot.snake[0],
                                                  pwrup.pos), pwrup) for
                                      pwrup in self.bot.game.
                                      pwrup_manager.get_powerups()])[1])
        # Add map potential and powerup potential together.
        self.pot_field = (self.target_pwrup.pot_field +
                          self.bot.game.tilemap.pot_field)

        self.no_pwrups = False
        # Fetch next tile from potential field
        self.next_tile = self.pot_field.get_next(self.bot.snake[0])

    def update(self, delta_time):
        if self.target_pwrup and self.bot.snake[0] == self.target_pwrup.pos:
            self.compute_pot_field()

        if self.no_pwrups:
            self.compute_pot_field()

        new_heading = sub_vecs(self.next_tile, self.bot.snake[0])
        self.bot.snake.set_heading(new_heading)

        if self.pot_field is not None:

            if self.next_tile == self.bot.snake[0]:
                # Print some stuff for debugging purposes.
                print('Next tile: {0}\nSnake: {1}\nTarget: {2}\n'.format(
                    self.next_tile, self.bot.snake[0], self.target_pwrup.pos))

                self.next_tile = self.pot_field.get_next(self.bot.snake[0])

    def enter(self):
        self.no_pwrups = (len(self.bot.game.pwrup_manager.get_powerups()) < 1)

    def leave(self):
        pass


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

    def update(self, delta_time):
        """Update fsm and player base."""

        self.curr_state.update(delta_time)
        PlayerBase.update(self, delta_time)
