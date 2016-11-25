# -*- coding: utf-8 -*-

"""
This module contains the base classes needed to build a finite state machine.
"""


from abc import ABCMeta, abstractmethod


class State(object):

    """
    Abstract class representing the base class for all State classes.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def enter(self, old_state):
        pass

    @abstractmethod
    def leave(self):
        pass


class FiniteStateMachine(object):

    """
    Abstract base class for a finite state machine.
    """

    __metaclass__ = ABCMeta

    def __init__(self, init_state=None):
        self.curr_state = init_state
        if init_state:
            self.curr_state.enter(None)

    def change_state(self, new_state):
        """
        Transition to another state by calling the 'leave' method
        of the current state and the 'enter' method for the new state.
        """
        old_state = self.curr_state
        if old_state:
            old_state.leave()
        self.curr_state = new_state
        self.curr_state.enter(old_state)
