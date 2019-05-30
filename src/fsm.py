# -*- coding: utf-8 -*-

"""
This module contains the base classes needed to build a finite state machine.
"""


from abc import ABCMeta, abstractmethod


class State(metaclass=ABCMeta):

    """
    Abstract class representing the base class for all State classes.
    """

    def enter(self):
        pass

    def leave(self):
        pass
    
    def pause(self):
        pass
        
    def resume(self):
        pass


class GameState(State, metaclass=ABCMeta):
    def __init__(self, game):
        self.game = game
        
    def update(self, dt):
        pass
        
    def draw(self):
        pass


class StateMachine(metaclass=ABCMeta):

    """
    Abstract base class for a finite state machine.
    """

    def __init__(self, init_state=None):
        self._stack = []
        
        if init_state:
            self.change_state(init_state)

    def push_state(self, new_state):
        if self._stack:
            self._stack[-1].pause()
        
        self._stack.append(new_state)
        self._stack[-1].enter()
        
    def pop_state(self):
        if self._stack:
            self._stack.pop().leave()
            
        if self._stack:
            self._stack[-1].resume()

    def change_state(self, new_state):
        if self._stack:
            self._stack[-1].leave()
            
        self._stack.append(new_state)
        self._stack[-1].enter()
        
    @property
    def current_state(self):
        if self._stack:
            return self._stack[-1]
            
        return None
