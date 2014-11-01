# -*- coding: utf-8 -*-
"""
Powerup module.
"""

from functools import partial
import xml.dom.minidom as dom

from utils import Timer


class Powerup(object):

    """
    Represents a powerup.
    """

    def __init__(self, game, pos, prototype):
        self.game = game
        self.pos = pos
        self.elapsed_lifetime = 0
        self.elapsed_blink = 0
        self.isalive = True
        self.isvisible = True
        self.tex = prototype['tex']
        self.actions = prototype['actions']
        self.lifetime = prototype.get('lifetime', 100000)
        self.blinkrate = prototype.get('blinkrate', 100000)
        self.startblinkingat = prototype.get('startblinkingat', 100000)
        self.autorespawn = prototype.get('autorespawn', False)
        self.reinit(pos, prototype)

    def reinit(self, pos, prototype):
        """Reinit powerup."""
        self.respawn(pos)
        self.tex = prototype['tex']
        self.actions = prototype['actions']
        self.lifetime = prototype.get('lifetime', 100000)
        self.blinkrate = prototype.get('blinkrate', 100000)
        self.startblinkingat = prototype.get('startblinkingat', 100000)
        self.autorespawn = prototype.get('autorespawn', False)

    def collect(self):
        """Tell the powerup that it has been collected."""
        self.isalive = False

    def respawn(self, pos):
        """Respawn powerup."""
        self.pos = pos
        self.elapsed_lifetime = 0
        self.elapsed_blink = 0
        self.isalive = True
        self.isvisible = True

    def update(self, delta_time):
        """Update powerup."""
        self.elapsed_lifetime += delta_time

        if self.elapsed_lifetime >= self.lifetime:
            self.isalive = False

        if self.elapsed_lifetime >= self.startblinkingat:
            self.elapsed_blink += delta_time
            if self.elapsed_blink >= self.blinkrate:
                self.elapsed_blink -= self.blinkrate
                self.isvisible = not self.isvisible

    def draw(self):
        """Draw powerup."""
        if self.isvisible:
            self.game.graphics.draw(self.tex, self.pos)


class PowerupManager(object):

    """
    Powerup manager.
    """

    def __init__(self, game):
        self.game = game
        self.pwrup_pool = []
        self.pwrup_spawners = []
        self.pwrup_prototypes = {}

        doc = dom.parse('../data/powerups.xml')

        for p_node in doc.firstChild.childNodes:
            if p_node.nodeName == 'Powerup':
                name = p_node.getAttribute('name')
                self.pwrup_prototypes[name] = {'actions': []}
                self.pwrup_prototypes[name]['tex'] = \
                    p_node.getAttribute('tex')
                self.pwrup_prototypes[name]['autorespawn'] = \
                    bool(p_node.getAttribute('autorespawn'))

                attrs = ('lifetime', 'blinkrate', 'startblinkingat')
                for attr in attrs:
                    if p_node.hasAttribute(attr):
                        self.pwrup_prototypes[name][attr] = \
                            float(p_node.getAttribute(attr))

                for node in p_node.childNodes:
                    if node.nodeName == 'action':
                        t_attr = node.getAttribute('target')
                        val_attr = node.getAttribute('value')
                        self.pwrup_prototypes[name]['actions'].append(
                            {'target': t_attr, 'value': float(val_attr)
                             if '.' in val_attr else int(val_attr)})

    def get_powerups(self):
        """Return all powerups stored in a tuple."""
        return tuple(self.pwrup_pool)

    def autospawn(self, config, freq, delay=0):
        """Register a powerup so it will be spawned automatically."""
        timer = Timer(1. / (freq / 60.),
                      partial(self.spawn_pwrup, config), delay, True)
        self.pwrup_spawners.append(timer)

    def spawn_pwrup(self, name, times=1):
        """Spawn powerup."""
        for _ in range(times):
            for pwrup in self.pwrup_pool:
                if not pwrup.isalive:
                    pwrup.reinit(self.game.randpos(),
                                 self.pwrup_prototypes[name])
                    return
            self.pwrup_pool.append(Powerup(self.game, self.game.randpos(),
                                           self.pwrup_prototypes[name]))

    def update(self, delta_time):
        """Update powerups."""
        for pwrup_spawner in self.pwrup_spawners:
            pwrup_spawner.update(delta_time)

        for pwrup in self.pwrup_pool:
            if pwrup.isalive:
                pwrup.update(delta_time)
            elif pwrup.autorespawn:
                pwrup.respawn(self.game.randpos())

    def draw(self):
        """Draw powerups."""
        for pwrup in self.pwrup_pool:
            if pwrup.isalive:
                pwrup.draw()
