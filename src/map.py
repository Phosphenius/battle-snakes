import xml.dom.minidom as dom
import os

import pygame

from settings import *
from utils import *
from snake import DIRECTIONS

class Map(object):
	def __init__(self, game, path):
		self.game = game
		self.tiles = []
		self.spawnpoints = []
		self.portals = {} # {p1:(p2, dir), p2:(p1, dir)}
		
		doc = dom.parse(path)
		maptag = doc.firstChild
		
		self.name = os.path.splitext(os.path.basename(path))[0]
		self.description = maptag.getAttribute('description')
		self.size_str = maptag.getAttribute('size')
		self.width = int(self.size_str.split('x')[0])
		self.height = int(self.size_str.split('x')[1])
		
		for node in maptag.childNodes:
			if node.nodeName == 'Tiles':
				self.tiles = str_to_vec_lst(node.firstChild.data)
			elif node.nodeName == 'Spawnpoints':
				self.spawnpoints = str_to_vec_lst(node.firstChild.data)
			elif node.nodeName == 'Portals':
				for portal_node in node.childNodes:
					if portal_node.nodeName == 'Portal':
						# Needs refactoring/improvement
						p1 = p2 = p1_dir = p2_dir = None
						for p_node in portal_node.childNodes:
							if p_node.nodeName == 'p1':
								p1 = str_to_vec(p_node.firstChild.data)
								p1_dir = \
								DIRECTIONS[p_node.getAttribute('dir')]
							elif p_node.nodeName == 'p2':
								p2 = str_to_vec(p_node.firstChild.data)
								p2_dir = \
								DIRECTIONS[p_node.getAttribute('dir')]
							if p1 is not None and p2 is not None:
								self.portals.update({p1:(p2, p2_dir),
													 p2:(p1, p1_dir)})
	def update(self, dt):
		pass
		
	def draw(self):
		for t in self.tiles:
			self.game.graphics.draw('wall', t)
			
		for sp in self.spawnpoints:
			self.game.graphics.draw('spawnpoint', sp)	
			
		for p in self.portals.values():
			self.game.graphics.draw('portal', p[0])
