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
		
		self.spawnpoints = []
		self.native_spawnpoints = {}
		self._map = []
		self.portals = {}
		
		self.spatialhash = defaultdict(list)
		
		maybe_portals = {}
		mapsurf = pygame.image.load('../data/maps/testmap1.png')
		mapdata = pygame.PixelArray(mapsurf)
		
		for y in range(ROWS):
			for x in range(COLS):
				if mapdata[x][y] == mapsurf.map_rgb(BLACK):
					self._map.append((x, y))
				elif mapdata[x][y] == mapsurf.map_rgb(GREEN):
					self.spawnpoints.append((x, y))
				elif mapdata[x][y] == mapsurf.map_rgb(PLAYER1['color']):
					self.spawnpoints.append((x, y))
					self.native_spawnpoints[PLAYER1['id']] = (x, y)
				elif mapdata[x][y] == mapsurf.map_rgb(PLAYER2['color']):
					self.spawnpoints.append((x, y))
					self.native_spawnpoints[PLAYER2['id']] = (x, y)
				elif mapdata[x][y] != mapsurf.map_rgb(WHITE):
					col = mapdata[x][y]
					if col not in maybe_portals:
						maybe_portals[col] = []
					maybe_portals[col].append((x, y))
					  
		for v in maybe_portals.values():
			if len(v) == 2:
				self.portals.update({v[0]:v[1], v[1]:v[0]})	
		
		# Create two players
		self.players = [Player(self, PLAYER1), Player(self, PLAYER2)]
		
		self.build_sh()
		
		for i in range(int(len(self.players)*5)):
			self.pwrup_manager.spawn_pwrup(FOOD1)
			
		for i in range(int(len(self.players)*2.5)):
			self.pwrup_manager.spawn_pwrup(FOOD2)
			
		for i in range(len(self.players)):
			self.pwrup_manager.spawn_pwrup(FOOD3)
			
		self.pwrup_manager.register_autospawn(EVILTHING, 12)
		self.pwrup_manager.register_autospawn(SPEEDUP1, 3)
		self.pwrup_manager.register_autospawn(SPEEDUP2, 1.5)
		self.pwrup_manager.register_autospawn(SHRINK1, 2.5)
		self.pwrup_manager.register_autospawn(SHRINK2, 1.8)
		self.pwrup_manager.register_autospawn(HEAL, 1.2)
		self.pwrup_manager.register_autospawn(JACKPOT, 1, 60)
		self.pwrup_manager.register_autospawn(LIFE, 0.75, 120)

	# Treats 'obj' as if the playfield was toroidal
	def toroidal(self, obj):
		x, y = obj
		if x < 0:
			obj = (COLS-1, y)
		if x > COLS-1:
			obj = (0, y)
		if y < 0:
			obj = (x, ROWS-1)
		if y > ROWS-1:
			obj = (x, 0)
		return obj
	
	def get_spawnpoint(self):
		return random.choice(filter(self.isfree, self.spawnpoints))
		
	def randpos(self):
		while True:
			pos = (random.randint(1, COLS-1), random.randint(1, ROWS-1))
			if pos not in self.spatialhash and pos not in self._map:
				return pos
	
	# Test if a cell is free or blocked by something
	def isfree(self, pos):
		return len(self.spatialhash.get(pos, [])) == 0
	
	def build_sh(self):
		self.spatialhash.clear()
		for k, v in self.portals.items():
			self.spatialhash[k].append((PORTAL_TAG, v))
			
		for p in self.pwrup_manager.pwrup_pool:
			if p.isalive:
				self.spatialhash[p.pos].append((PWRUP_TAG, p))
			
		for s in self.shot_manager.shot_pool:
			if s.isalive:
				self.spatialhash[s.pos].append((SHOT_TAG, s))
			
		for p in self.players:
			self.spatialhash[p.snake[0]].append((p.snake.head_tag, 
			p.snake))
			for s in p.snake[1:]:
				self.spatialhash[s].append((p.snake.body_tag, p.snake))
		
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
			if p.snake[0] in self._map:
				p.snake.take_damage(20, WALL_TAG, True, True, 1, 
				shrink=0, slowdown=0.07)
				break
					
		for s in self.shot_manager.shot_pool:
			if s.pos in self._map:
				s.hit()
			if s.pos in self.portals:
				s.pos = add_vecs(self.portals[s.pos], s.heading)
					
		for k, v in self.spatialhash.items():
			if len(v) > 1:
				for p in self.players:
					for tag, obj in v:
						if tag == p.snake.head_tag:
							p.coll_check_head(v)
						if tag == p.snake.body_tag:
							p.coll_check_body(v)

	def draw(self):
		for p in self.spawnpoints:
			self.graphics.draw('spawnpoint', p)
		
		for p in self.portals.values():
			self.graphics.draw('portal', p)
			
		for b in self._map:
			self.graphics.draw('wall', b)	
		
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
