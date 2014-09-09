#!/usr/bin/python2

# Converts PNG + XML maps found in MAP_SRC_DIR into pure XML and stores 
# them in MAP_DEST_DIR.

import xml.dom.minidom as dom
import os
import shutil

import pygame

from colors import *

MAP_SRC_DIR = '../data/mapsources'
MAP_DEST_DIR = '../data/maps'

def main():
	for mf in os.listdir(MAP_SRC_DIR):
		src = os.path.join(MAP_SRC_DIR, mf)
		dest = os.path.join(MAP_DEST_DIR, mf + '.xml')
		
		if os.path.exists(dest):
			os.remove(dest)
			
		shutil.copy(os.path.join(src, 'map.xml'), MAP_DEST_DIR)
		os.rename(os.path.join(MAP_DEST_DIR, 'map.xml'), 
				  os.path.join(MAP_DEST_DIR, 
				  os.path.basename(src) + '.xml'))
				  
		doc = dom.parse(dest)
		maptag = doc.firstChild
		
		mapsurf = pygame.image.load(os.path.join(src, 'map.png'))
		mapdata = pygame.PixelArray(mapsurf)
		w, h = mapsurf.get_size()	
		tiles = []
		spawnpoints = []
		
		size_attr = dom.Attr('size')
		size_attr.value = '{0}x{1}'.format(w, h)
		maptag.setAttributeNode(size_attr)
		
		for y in range(h):
			for x in range(w):
				if mapdata[x][y] == mapsurf.map_rgb(WHITE):
					tiles.append((x, y))
				elif mapdata[x][y] == mapsurf.map_rgb(BLUE):
					spawnpoints.append((x, y))
		
		sp_tag = dom.Element('Spawnpoints')
		tile_tag = dom.Element('Tiles')
		
		str_sp = ''
		for i, sp in enumerate(spawnpoints):
			if i != 0:
				str_sp += ';{0}:{1}'.format(*sp)
			else:
				str_sp += '{0}:{1}'.format(*sp)
				
		text_sp = dom.Text()
		text_sp.data = str_sp
		
		str_tiles = ''
		for i, t in enumerate(tiles):
			if i != 0:
				str_tiles += ';{0}:{1}'.format(*t)
			else:
				str_tiles += '{0}:{1}'.format(*t)
				
		text_t = dom.Text()
		text_t.data = str_tiles
		
		sp_tag.appendChild(text_sp)
		tile_tag.appendChild(text_t)
		maptag.appendChild(sp_tag)
		maptag.appendChild(tile_tag)
		
		with open(dest, 'w') as f:
			doc.writexml(f)
	
if __name__ == '__main__': main()
