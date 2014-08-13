from functools import partial
from utils import Timer
from settings import PWRUP_TAG

# -- Powerups --
FOOD1 = {'tex':'food1', 'grow':1, 'points':12, 'speedgain':0.12, 
'hitpoints':5, 'autorespawn':True, 'boostgain':100}
FOOD2 = {'tex':'food2', 'grow':1, 'points':25, 'speedgain':0.21, 
'hitpoints':10, 'autorespawn':True, 'boostgain':180}
FOOD3 = {'tex':'food3', 'points':50, 'speedgain':0.45, 'hitpoints':42,
'autorespawn':True, 'boostgain':240}
EVILTHING = {'tex':'evilthing', 'points':-35, 'speedgain':-0.5,
'damage':30, 'grow':2, 'lifetime':10, 'blinkrate':0.25,
'startblinkingat':8, 'boostgain':-100000}
SPEEDUP1 = {'tex':'speedup1', 'points':1, 'speedgain':0.8, 'lifetime':10,
'startblinkingat':7, 'blinkrate':0.5, 'boostgain':100000}
SPEEDUP2 = {'tex':'speedup2', 'points':3, 'speedgain':1.2, 'lifetime':8,
'startblinkingat':6.5, 'blinkrate':0.35, 'boostgain':100000}
SHRINK1 = {'tex':'shrink1', 'points':5, 'grow':-2, 'lifetime':15,
'startbliningat':10, 'blinkrate':0.75}
SHRINK2 = {'tex':'shrink2', 'points':10, 'grow':-5, 'lifetime':11,
'startblinkingat':9, 'blinkrate':0.4}
HEAL = {'tex':'heal', 'points':8, 'speedgain':0.15, 'hitpoints':450,
'lifetime':20, 'startblinkingat':18, 'blinkrate':0.3, 'boostgain':100000}
JACKPOT = {'tex':'jackpot', 'points':250, 'lifes':1, 'hitpoints':500,
'lifetime':20, 'startblinkingat':15, 'blinkrate':0.25}
LIFE = {'tex':'life', 'lifes':1, 'lifetime':15, 'startblinkingat':14,
'blinkrate':0.1}

class Powerup:
	def __init__(self, game, pos, config):
		self.game = game
		self.pos = pos
		self.elapsed_lifetime = 0
		self.elapsed_blink = 0
		self.isalive = True
		self.isvisible = True
		self.reinit(pos, config)
		
	def reinit(self, pos, config):
		self.respawn(pos)
		self.tex = config['tex']
		self.lifetime = config.get('lifetime', 100000)
		self.blinkrate = config.get('blinkrate', 100000)
		self.startblinkingat = config.get('startblinkingat', 100000)
		self.speedgain = config.get('speedgain', 0)
		self.boostgain = config.get('boostgain', 0)
		self.grow = config.get('grow', 0)
		self.points = config.get('points', 0)
		self.hitpoints = config.get('hitpoints', 0)
		self.lifes = config.get('lifes', 0)
		self.damage = config.get('damage', 0)
		self.autorespawn = config.get('autorespawn', False)
		
	def collect(self):
		self.isalive = False
		
	def respawn(self, pos):
		self.pos = pos
		self.elapsed_lifetime = 0
		self.elapsed_blink = 0
		self.isalive = True
		self.isvisible = True
	
	def update(self, dt):
		self.elapsed_lifetime += dt
		
		if self.elapsed_lifetime >= self.lifetime:
			self.isalive = False
			
		if self.elapsed_lifetime >= self.startblinkingat:
			self.elapsed_blink += dt
			if self.elapsed_blink >= self.blinkrate:
				self.elapsed_blink -= self.blinkrate
				self.isvisible = not self.isvisible
		
	def draw(self):
		if self.isvisible:
			self.game.graphics.draw(self.tex, self.pos)
		
class PowerupManager:
	def __init__(self, game):
		self.game = game
		self.pwrup_pool = []
		self.pwrup_spawners = []
		
	def register_autospawn(self, config, freq, delay=0):
		t = Timer(1. / (freq / 60.),  
		partial(self.spawn_pwrup, config), delay, True)
		self.pwrup_spawners.append(t)
		
	def spawn_pwrup(self, config):
		for p in self.pwrup_pool:
			if not p.isalive:
				p.reinit(self.game.randpos(), config)
				return
		self.pwrup_pool.append(Powerup(self.game, self.game.randpos(),
		config))
		
	def update(self, dt):
		for p in self.pwrup_spawners:
			p.update(dt)
			
		for p in self.pwrup_pool:
			if p.isalive:
				p.update(dt)
			elif p.autorespawn:
				p.respawn(self.game.randpos())
		
	def draw(self):
		for p in self.pwrup_pool:
			if p.isalive:
				p.draw()
