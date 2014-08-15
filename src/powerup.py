from functools import partial
import xml.dom.minidom as dom
import os

from utils import Timer
from settings import PWRUP_TAG

class Powerup:
	def __init__(self, game, pos, prototype):
		self.game = game
		self.pos = pos
		self.elapsed_lifetime = 0
		self.elapsed_blink = 0
		self.isalive = True
		self.isvisible = True
		self.reinit(pos, prototype)
		
	def reinit(self, pos, prototype):
		self.respawn(pos)
		self.tex = prototype['tex']
		self.actions = prototype['actions']
		self.lifetime = prototype.get('lifetime', 100000)
		self.blinkrate = prototype.get('blinkrate', 100000)
		self.startblinkingat = prototype.get('startblinkingat', 100000)
		self.autorespawn = prototype.get('autorespawn', False)
		
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
		self.pwrup_prototypes = {}
		
		doc = dom.parse('../data/powerups.xml')
		
		for p_node in doc.firstChild.childNodes:
			if p_node.nodeName == 'Powerup':
				name = p_node.getAttribute('name')
				self.pwrup_prototypes[name] = {'actions':[]}
				self.pwrup_prototypes[name]['tex'] = \
				p_node.getAttribute('tex')
				self.pwrup_prototypes[name]['autorespawn'] = \
				bool(p_node.getAttribute('autorespawn'))
				
				for node in p_node.childNodes:
					if node.nodeName == 'action':
						t_attr = node.getAttribute('target')
						val_attr = node.getAttribute('value')
						self.pwrup_prototypes[name]['actions'].append(
						{'target':t_attr,
						'value':float(val_attr) if '.' in val_attr else int(val_attr)})		
		
	def autospawn(self, config, freq, delay=0):
		t = Timer(1. / (freq / 60.),  
		partial(self.spawn_pwrup, config), delay, True)
		self.pwrup_spawners.append(t)
		
	def spawn_pwrup(self, name):
		for p in self.pwrup_pool:
			if not p.isalive:
				p.reinit(self.game.randpos(), self.pwrup_prototypes[name])
				return
		self.pwrup_pool.append(Powerup(self.game, self.game.randpos(),
		self.pwrup_prototypes[name]))
		
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
