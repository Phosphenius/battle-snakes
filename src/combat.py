from utils import *

# Shots
MG_SHOT1 = {'tex':'mg_shot1', 'speed':42, 'damage':10}
SHOT1 = {'tex':'shot1', 'speed':50, 'damage':100, 'blinkrate':0.06}
SHOT2 = {'tex':'shot2', 'speed':27, 'damage':25, 'slowdown':2.5}

# Weapons
STD_MG = {'shot':MG_SHOT1, 'type':'std_mg', 'ammo':100000, 'freq':5}

class Shot:
	def __init__(self, game, pos, heading, tag, config):
		self.game = game
		self.tex = config['tex']
		self.reinit(pos, heading, tag, config)
		
	def reinit(self, pos, heading, tag, config):
		self.isalive = True
		self.isvisible = True
		self.elapsed_t = 0
		self.elapsed_blink = 0
		self.pos = pos
		self.heading = heading
		self.tag = tag
		self.damage = config.get('damage', 0)
		self.speed = 1. / config['speed']
		self.slowdown = config.get('slowdown', 0)
		self.blinkrate = config.get('blinkrate', 100000)
		
	def hit(self):
		self.isalive = False
		
	def update(self, dt):
		self.elapsed_t += dt
		self.elapsed_blink += dt
		
		if self.elapsed_t >= self.speed:
			self.elapsed_t -= self.speed
			self.pos = add_vecs(self.pos, self.heading)
			self.pos = self.game.toroidal(self.pos)
			
		if self.elapsed_blink >= self.blinkrate:
			self.elapsed_blink -= self.blinkrate
			self.isvisible = not self.isvisible
			
	def draw(self):
		if self.isvisible:
			self.game.graphics.draw(self.tex, self.pos)
		
class ShotManager:
	def __init__(self, game):
		self.game = game
		self.shot_pool = []
		
	def create_shot(self, pos, heading, tag, config):
		for s in self.shot_pool:
			if not s.isalive:
				s.reinit(pos, heading, tag, config)
				return
		self.shot_pool.append(Shot(self.game, pos, heading, tag, config))
		
	def update(self, dt):
		for s in self.shot_pool:
			if s.isalive:
				s.update(dt)
		
	def draw(self):
		for s in self.shot_pool:
			if s.isalive:
				s.draw()
				
class Weapon:
	def __init__(self, config):
		self.ammo = config['ammo']
		self.shot = config['shot']
		self._type = config['type']
		self.firerate = 1. / config['freq']
		self.elapsed_t = self.firerate - 1
		self.firing = False
		
	def set_firing(self, value):
		if value:
			self.elapsed_t = self.firerate - 1
		self.firing = value
		
	def update(self, dt):
		if self.firing:
			self.elapsed_t += dt
