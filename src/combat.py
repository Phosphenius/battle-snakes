"""
Combat module.
"""

from utils import add_vecs, mul_vec

# Shots
MG_SHOT1 = {'tex':'mg_shot1', 'speed':42, 'damage':10}
SHOT1 = {'tex':'shot1', 'speed':70, 'damage':100}
PLASMA_SHOT = {'tex':'shot2', 'speed':30, 'damage':25, 'slowdown':2.5}

# Weapons
STD_MG = {'shot':MG_SHOT1, 'type':'MG', 'ammo':999999, 'freq':8}
H_GUN = {'shot':SHOT1, 'type':'Cannon', 'ammo':20, 'freq':1.3}
PLASMA_GUN = {'shot':PLASMA_SHOT, 'type':'Plasma', 'ammo':50, 'freq':2.5}

DEFAULT_SHOT_BLINK_RATE = 100000
DEFAULT_SHOT_LIFETIME = 5

class Shot(object):
    """Represents a shot."""
    def __init__(self, game, pos, heading, tag, config):
        self.game = game
        self.isalive = True
        self.isvisible = True
        self.elapsed_t = 0
        self.elapsed_blink = 0
        self.elapsed_lifetime = 0
        self.pos = pos
        self.heading = heading
        self.tag = tag
        self.tex = config['tex']
        self.damage = config.get('damage', 0)
        self.speed = 1. / config['speed']
        self.slowdown = config.get('slowdown', 0)
        self.blinkrate = config.get('blinkrate', DEFAULT_SHOT_BLINK_RATE)
        self.lifetime = config.get('lifetime', DEFAULT_SHOT_LIFETIME)

        self.reinit(pos, heading, tag, config)

    def reinit(self, pos, heading, tag, config):
        """Reinit shot."""
        self.isalive = True
        self.isvisible = True
        self.elapsed_t = 0
        self.elapsed_blink = 0
        self.elapsed_lifetime = 0
        self.pos = pos
        self.heading = heading
        self.tag = tag
        self.tex = config['tex']
        self.damage = config.get('damage', 0)
        self.speed = 1. / config['speed']
        self.slowdown = config.get('slowdown', 0)
        self.blinkrate = config.get('blinkrate', DEFAULT_SHOT_BLINK_RATE)
        self.lifetime = config.get('lifetime', DEFAULT_SHOT_LIFETIME)

    def hit(self):
        """Tell the shot that it has hit something."""
        self.isalive = False

    def update(self, delta_time):
        """Update shot."""
        self.elapsed_t += delta_time
        self.elapsed_blink += delta_time
        self.elapsed_lifetime += delta_time

        if self.elapsed_t >= self.speed:
            self.elapsed_t -= self.speed
            self.pos = add_vecs(self.pos, self.heading)
            self.pos = self.game.toroidal(self.pos)

        if self.elapsed_blink >= self.blinkrate:
            self.elapsed_blink -= self.blinkrate
            self.isvisible = not self.isvisible
            
        if self.elapsed_lifetime >= self.lifetime:
            self.hit()

    def draw(self):
        """Draw shot."""
        if self.isvisible:
            self.game.graphics.draw(self.tex, self.pos)

class ShotManager(object):

    """
    Shot manager.
    """

    def __init__(self, game):
        self.game = game
        self.shot_pool = []

    def create_shot(self, pos, heading, tag, config):
        """Create shot."""
        for shot in self.shot_pool:
            if not shot.isalive:
                shot.reinit(pos, heading, tag, config)
                return
        self.shot_pool.append(Shot(self.game, pos, heading, tag, config))

    def update(self, delta_time):
        """Update shots."""
        for shot in self.shot_pool:
            if shot.isalive:
                shot.update(delta_time)

    def draw(self):
        """Draw shots."""
        for shot in self.shot_pool:
            if shot.isalive:
                shot.draw()

class Weapon(object):

    """
    Represents a weapon.
    """

    def __init__(self, game, owner, config):
        self.game = game
        self.owner = owner
        self.ammo = config['ammo']
        self.shot = config['shot']
        self._type = config['type']
        self.firerate = 1. / config['freq']
        self.elapsed_t = 0
        self.firing = False

    def set_firing(self, value):
        """Set 'firing' property."""
        self.firing = value

    def update(self, delta_time):
        """Update weapon."""
        if self.firing:
            self.elapsed_t += delta_time

        if self.elapsed_t >= self.firerate:
            self.elapsed_t -= self.firerate
            if self.ammo > 0:
                if self.owner.snake.heading is not None:
                    head = self.owner.snake[0]
                    heading = self.owner.snake.heading

                    if add_vecs(head, mul_vec(heading, 1)) not in \
                    self.game._map.tiles and \
                    head not in self.game._map.tiles:
                        self.ammo -= 1
                        self.game.shot_manager.create_shot(
                        add_vecs(head, mul_vec(heading, 2)),
                        heading, self.owner.snake.head_tag, self.shot)
            else:
                self.firing = False

