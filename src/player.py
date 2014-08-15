from collections import deque

import pygame
from pygame.locals import *

from colors import *
from snake import *
from utils import *
from combat import *
from settings import *

# -- Controls --
CTRLS1 = {'left':K_LEFT, 'right':K_RIGHT, 'up':K_UP, 'down':K_DOWN,
'action':K_l, 'boost':K_k, 'nextweapon':K_j}
CTRLS2 = {'left':K_a, 'right':K_d, 'up':K_w, 'down':K_s, 'action':K_f,
'boost':K_g, 'nextweapon':K_h}

# -- Players --
PLAYER1 = {'id':'1', 'color':BLUE, 'ctrls':CTRLS1, 
'tex':'snake_body_p1'}
PLAYER2 = {'id':'2', 'color':RED, 'ctrls':CTRLS2, 
'tex':'snake_body_p2'}

class Player(object):
	def __init__(self, game, config):
		self.game = game
		self.game.key_manager.key_down_event.append(self.key_down)
		self.game.key_manager.key_up_event.append(self.key_up)
		self.ctrls = config['ctrls']
		self._id = config['id']	
		self.color = config['color']
		self.snake = Snake(game, game.native_spawnpoints[self._id], 
		config['tex'], self._id, self.snake_killed)
		self._lifes = INIT_LIFES
		self.points = 0
		self._boost = INIT_BOOST
		self.boosting = False
		self.saved_speed = None
		self.weapons = deque((
		Weapon(self.game, self, STD_MG), 
		Weapon(self.game, self, H_GUN), 
		Weapon(self.game, self, PLASMA_GUN)))
		self.pwrup_targets = {
		'points':'points', 'grow' :'snake.grow', 'speed':'snake.speed',
		'boost' :'boost' , 'lifes':'lifes', 
		'hp':'snake.hitpoints'}
		
	@property
	def lifes(self):
		return self._lifes
	
	@lifes.setter
	def lifes(self, value):
		if value > MAX_LIFES:
			self._lifes = MAX_LIFES
		elif value < 0:
			self._lifes = 0
		else:
			self._lifes = value
		
	@property
	def boost(self):
		return self._boost
		
	@boost.setter
	def boost(self, value):
		if value > MAX_BOOST:
			self._boost = MAX_BOOST
		elif value < 0:
			self._boost = 0
		else:
			self._boost = value
		
	def set_lifes(self, lifes):
		self.lifes = MAX_LIFES if lifes > MAX_LIFES else lifes
		
	def coll_check_head(self, collobjs):
		for tag, obj in collobjs:
			if (tag.endswith('-body') or tag.endswith('-head')) and \
			tag != self.snake.head_tag:
				obj.take_damage(35, self.snake.head_tag, False, True, 
				0.7, shrink=1, slowdown=0.03)
			elif tag == PORTAL_TAG:
				self.snake[0] = add_vecs(obj, self.snake.heading)
			elif tag == PWRUP_TAG:
				for a in obj.actions:
					target = self.pwrup_targets[a['target']]
					if '.' in target:
						t1, t2 = target.split('.')
						attr = getattr(getattr(self, t1), t2)
						setattr(getattr(self, t1), t2, attr + a['value'])
					else:
						attr = getattr(self, target)
						setattr(self, target, attr + a['value'])
				obj.collect()
			elif tag == SHOT_TAG:
				self.handle_shot(obj)
				
	def coll_check_body(self, collobjs):
		for tag, obj in collobjs:
			if tag == SHOT_TAG:
				self.handle_shot(obj)
		
	def handle_shot(self, shot):
		self.snake.take_damage(shot.damage, shot.tag, False, True, 1.2,
		slowdown=shot.slowdown, shrink=1)
		shot.hit()
		
	def key_down(self, key):
		if key == self.ctrls['boost']:
			self.boosting = True
			self.saved_speed = self.snake.speed
			self.snake._speed = BOOST_SPEED
		elif key == self.ctrls['action']:
			# Has the potential to cause an endless loop. 
			while self.weapons[0].ammo <= 0:
				self.weapons.rotate(1)
			self.weapons[0].set_firing(True)
		
	def key_up(self, key):
		if key == self.ctrls['boost']:
			self.boosting = False
			self.snake.speed = self.saved_speed
		elif key == self.ctrls['action']:
			self.weapons[0].set_firing(False)
		
	def update(self, dt):
		self.snake.update(dt)
			
		self.weapons[0].update(dt)
		
		if self.game.key_manager.key_pressed(self.ctrls['left']) \
		and self.snake.heading != RIGHT:
			self.snake.set_heading(LEFT)
		elif self.game.key_manager.key_pressed(self.ctrls['up']) \
		and self.snake.heading != DOWN:
			self.snake.set_heading(UP)
		elif self.game.key_manager.key_pressed(self.ctrls['down']) \
		and self.snake.heading != UP:
			self.snake.set_heading(DOWN)
		elif self.game.key_manager.key_pressed(self.ctrls['right']) \
		and self.snake.heading != LEFT:
			self.snake.set_heading(RIGHT)
			
		if self.game.key_manager.key_tapped(self.ctrls['nextweapon']):
			# Dangerous... 
			self.weapons.rotate(1)
			while self.weapons[0].ammo <= 0:
				self.weapons.rotate(1)
			
		if self.snake.heading != self.snake.prev_heading:
			self.snake.ismoving = True
			
		if self.boost < BOOST_COST * dt:
			self.boosting = False
			self.snake.speed = self.saved_speed
		
		if self.boosting:
			b = self.boost - BOOST_COST * dt
			if b < BOOST_COST * dt:
				self.boost = 0
			else:
				self.boost = b
		else:
			self.boost = self.boost + BOOST_GAIN * dt
		
	def snake_killed(self, by):
		if self.lifes > 0:
			self.lifes -= 1
			self.boost = MAX_BOOST
			self.snake.respawn(self.game.get_spawnpoint())
		
	def draw(self, offset):
		self.snake.draw()
		self.game.draw_string('Player{0}'.format(self._id),
		add_vecs((2, 2), offset), self.color)
		self.game.draw_string('{0:.2f}'.format(self.snake.speed),
		add_vecs((56, 2), offset), WHITE)
		self.game.draw_string('Points: {0}'.format(self.points), 
		add_vecs((2, 18), offset), WHITE)
		
		pygame.draw.rect(self.game.screen, ORANGE, 
		pygame.Rect(add_vecs((100, 2), offset), (104, 20)))
		
		pygame.draw.rect(self.game.screen, RED,
		pygame.Rect(add_vecs((102, 4), offset), (int(
		self.snake.hitpoints / float(MAX_HITPOINTS) * 100), 7)))
		
		pygame.draw.rect(self.game.screen, BLUE,
		pygame.Rect(add_vecs((102, 13), offset), (int(
		self.boost / float(MAX_BOOST) * 100), 7)))
		
		self.game.draw_string('{0} {1}'.format(self.weapons[0]._type, 
		self.weapons[0].ammo), 
		add_vecs((208, 2), offset), WHITE)
		
		for i in range(self.lifes):
			self.game.graphics.draw('life16x16', add_vecs((100, 24), 
			offset), gridcoords=False, offset=(i*18, 0))
