from utils import *

# Shots
MG_SHOT1 = {'tex':'mg_shot1', 'speed':42, 'damage':10}
SHOT1 = {'tex':'shot1', 'speed':70, 'damage':100}
PLASMA_SHOT = {'tex':'shot2', 'speed':30, 'damage':25, 'slowdown':2.5}

# Weapons
STD_MG = {'shot':MG_SHOT1, 'type':'std_mg', 'ammo':9999, 'freq':8}
H_GUN = {'shot':SHOT1, 'type':'h_gun', 'ammo':35, 'freq':1.3}
PLASMA_GUN = {'shot':PLASMA_SHOT, 'type':'plasma', 'ammo':50, 'freq':2.5}

class Shot:
	def __init__(self, game, pos, heading, tag, config):
		self.game = game
		self.reinit(pos, heading, tag, config)
		
	def reinit(self, pos, heading, tag, config):
		self.isalive = True
		self.isvisible = True
		self.elapsed_t = 0
		self.elapsed_blink = 0
		self.pos = pos
		self.heading = heading
		self.tag = tag
		self.tex = config['tex']
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
		self.firing = value
		
	def update(self, dt):
		if self.firing:
			self.elapsed_t += dt
			
		if self.elapsed_t >= self.firerate:
			self.elapsed_t -= self.firerate
			if self.ammo > 0:
				if self.owner.snake.heading is not None:
					self.ammo -= 1
					self.game.shot_manager.create_shot(
					
					add_vecs(self.owner.snake[0], 
					mul_vec(self.owner.snake.heading, 2)), 
					
					self.owner.snake.heading, self.owner.snake.head_tag, 
					self.shot)
			else:
				self.firing = False
	
