#!/usr/bin/env python

import sys
import glob
import os
import random
from collections import defaultdict

import cProfile

import pygame
from pygame.locals import *  

from colors import *
from utils import *
from powerup import *
from snake import *
from player import *
from combat import *
from map import *

VERSION = 'v0.1.0'

class GraphicsManager:
	def __init__(self, surf):
		self.surf = surf
		self.textures = {}
		for i in glob.glob('../gfx/*.png'):
			self.textures[os.path.splitext(os.path.split(i)[1])[0]] = \
			pygame.image.load(i)
		
	def draw(self, tex_name, pos, gridcoords=True, offset=(0, PANEL_H)):
		if tex_name not in self.textures:
			raise Exception('No such texture: {0}'.format(tex_name))
		if gridcoords:
			self.surf.blit(self.textures[tex_name], 
			add_vecs(mul_vec(pos, CELL_SIZE), offset))
		else:
			self.surf.blit(self.textures[tex_name], add_vecs(pos, offset))

class KeyManager:
	def __init__(self):
		self.curr_key_state = pygame.key.get_pressed()
		self.prev_key_state = None
		self.any_key_pressed = False
		self.key_down_event = []
		self.key_up_event = []
		
	def update(self):
		self.prev_key_state = self.curr_key_state
		self.curr_key_state = pygame.key.get_pressed()
		self.any_key_pressed = any(self.curr_key_state)
		
		for k in range(len(self.curr_key_state)):
			if self.curr_key_state[k] and not self.prev_key_state[k]:
				self.on_key_down(k)
			elif not self.curr_key_state[k] and self.prev_key_state[k]:
				self.on_key_up(k)
		
	def key_pressed(self, key):
		return self.curr_key_state[key]
	
	def key_tapped(self, key):
		return not self.curr_key_state[key] and self.prev_key_state[key]
	
	# Determines if any of the keys passed as an argument is pressed
	def any_pressed(self, *keys):
		return any([self.curr_key_state[k] for k in keys])
		
	def any_tapped(self, *keys):
		return any([not self.curr_key_state[k] and \
		self.prev_key_state[k] for k in keys])
		
	def on_key_up(self, key):
		for e in self.key_up_event:
			if e is not None:
				e(key)
		
	def on_key_down(self, key):
		for e in self.key_down_event:
			if e is not None:
				e(key)
		
class Game1:
	def __init__(self, res):
		random.seed()
		pygame.init()
		pygame.display.set_caption("Battle Snakes {0}".format(VERSION))
		
		self.sysfont = pygame.font.SysFont('Arial', 14)
		self.screen = pygame.display.set_mode(res)
		self.fpsClock = pygame.time.Clock() 
		self.key_manager = KeyManager()
		self.graphics = GraphicsManager(self.screen)
		self.pwrup_manager = PowerupManager(self)
		self.shot_manager = ShotManager(self)
		self._map = Map(self, '../data/maps/map01.xml')
		
		self.spatialhash = defaultdict(list)
		
		self.players = []
		self.build_sh()
		self.players.append(Player(self, PLAYER1))
		self.build_sh()
		self.players.append(Player(self, PLAYER2))
		
		for i in range(int(len(self.players)*5)):
			self.pwrup_manager.spawn_pwrup('food1')
			
		for i in range(int(len(self.players)*2.5)):
			self.pwrup_manager.spawn_pwrup('food2')
			
		for i in range(len(self.players)):
			self.pwrup_manager.spawn_pwrup('food3')
			
		self.pwrup_manager.autospawn('evilthing', 12)
		self.pwrup_manager.autospawn('speedup1', 2)
		self.pwrup_manager.autospawn('heal', 1.2)
		self.pwrup_manager.autospawn('jackpot', 1, 60)
		self.pwrup_manager.autospawn('life', 0.75, 120)

	# Treats 'obj' as if the playfield was toroidal
	def toroidal(self, obj):
		x, y = obj
		if x < 0:
			obj = (self._map.width-1, y)
		if x > self._map.width-1:
			obj = (0, y)
		if y < 0:
			obj = (x, self._map.height-1)
		if y > self._map.height-1:
			obj = (x, 0)
		return obj
	
	# Returns a random, unblocked spawnpoint
	def get_spawnpoint(self):
		return random.choice(filter(self.sp_unblocked, 
		self._map.spawnpoints))
		
	def randpos(self):
		while True:
			pos = (random.randint(1, self._map.width-1), 
			random.randint(1, self._map.height-1))
			if pos not in self.spatialhash and pos not in self._map.tiles:
				return pos
	
	# Test if a cell is blocked by something
	def isunblocked(self, pos):
		return len(self.spatialhash.get(pos, [])) == 0
		
	# Determines if a spawnpoint is blocked
	def sp_unblocked(self, sp):
		return len(self.spatialhash[sp]) == 1
	
	# Build the spatial hash used for collision detection
	# Map data is never put into the sh since it never changes
	def build_sh(self, include_players=True):
		self.spatialhash.clear()
			
		# Add spawnpoints (So powerups don't appear on them)
		for sp in self._map.spawnpoints:
			self.spatialhash[sp].append((SPAWNPOINT_TAG, sp))
		
		# Add portals
		for k, v in self._map.portals.items():
			self.spatialhash[k].append((PORTAL_TAG, v))
			
		# Add powerups 
		for p in self.pwrup_manager.pwrup_pool:
			if p.isalive:
				self.spatialhash[p.pos].append((PWRUP_TAG, p))
		
		# Add shots
		for s in self.shot_manager.shot_pool:
			if s.isalive:
				self.spatialhash[s.pos].append((SHOT_TAG, s))
		
		# Add snakes
		for p in self.players:
			self.spatialhash[p.snake[0]].append((p.snake.head_tag, 
			p.snake))
			for s in p.snake[1:]:
				self.spatialhash[s].append((p.snake.body_tag, 
				p.snake))
		
	def update(self, dt):
		self.key_manager.update()

		self.pwrup_manager.update(dt)
		self.shot_manager.update(dt)
		
		for p in self.players:
			p.update(dt) 
		
		self.build_sh()
		
		if self.key_manager.any_pressed(K_q, K_ESCAPE):
			self.quit()
				
		for p in self.players:
			if p.snake[0] in self._map.tiles:
				p.snake.take_damage(20, WALL_TAG, True, True, 1, 
				shrink=0, slowdown=0.07)
				break
					
		for s in self.shot_manager.shot_pool:
			if s.pos in self._map.tiles:
				s.hit()
			if s.pos in self._map.portals:
				s.heading = self._map.portals[s.pos][1]
				s.pos = add_vecs(self._map.portals[s.pos][0], s.heading)
					
		for k, v in self.spatialhash.items():
			if len(v) > 1:
				for p in self.players:
					for tag, obj in v:
						if tag == p.snake.head_tag:
							p.coll_check_head(v)
						if tag == p.snake.body_tag:
							p.coll_check_body(v)

	def draw(self):
		self._map.draw()
		
		self.pwrup_manager.draw()
		self.shot_manager.draw()
		
		pygame.draw.rect(self.screen, (32, 32, 32), 
		pygame.Rect(0, 0, SCR_W, PANEL_H))
	
		for i, p in enumerate(self.players):
			p.draw(mul_vec((290, 0), i))
			
		self.draw_string('FPS: {0:.2f}'.
		format(self.fpsClock.get_fps()), (1200, 2), WHITE)
			
	def draw_string(self, text, pos, color):
		self.screen.blit(self.sysfont.render(text, True, color), pos)
	
	def Run(self):
		while True:
			for event in pygame.event.get():
				if event.type == QUIT:
					self.quit()
			self.screen.fill(BLACK)
			dt = self.fpsClock.tick() / 1000.0
			self.update(dt)
			self.draw()
			pygame.display.update()
			
	def quit(self):
		pygame.quit()
		sys.exit()

def main():
	g = Game1((SCR_W, SCR_H))
	g.Run()

if __name__ == '__main__': main()
#if __name__ == '__main__': cProfile.run('main()')
