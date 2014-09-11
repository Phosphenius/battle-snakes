#!/usr/bin/python2

"""
Map converter

Converts PNG + XML maps found in MAP_SRC_DIR into pure XML and stores
them in MAP_DEST_DIR.
"""

import xml.dom.minidom as dom
import os
import shutil

import pygame

from colors import WHITE, BLUE

MAP_SRC_DIR = '../data/mapsources'
MAP_DEST_DIR = '../data/maps'

def main():
    """Here is where the magic happens."""
    for mapfolder in os.listdir(MAP_SRC_DIR):
        src = os.path.join(MAP_SRC_DIR, mapfolder)
        dest = os.path.join(MAP_DEST_DIR, mapfolder + '.xml')

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
        width, height = mapsurf.get_size()
        tiles = []
        spawnpoints = []

        size_attr = dom.Attr('size')
        size_attr.value = '{0}x{1}'.format(width, height)
        maptag.setAttributeNode(size_attr)

        for row in range(height):
            for col in range(width):
                if mapdata[col][row] == mapsurf.map_rgb(WHITE):
                    tiles.append((col, row))
                elif mapdata[col][row] == mapsurf.map_rgb(BLUE):
                    spawnpoints.append((col, row))

        sp_tag = dom.Element('Spawnpoints')
        tile_tag = dom.Element('Tiles')

        str_sp = ''
        for i, spawnpoint in enumerate(spawnpoints):
            if i != 0:
                str_sp += ';{0}:{1}'.format(*spawnpoint)
            else:
                str_sp += '{0}:{1}'.format(*spawnpoint)

        text_sp = dom.Text()
        text_sp.data = str_sp

        str_tiles = ''
        for i, tile in enumerate(tiles):
            if i != 0:
                str_tiles += ';{0}:{1}'.format(*tile)
            else:
                str_tiles += '{0}:{1}'.format(*tile)

        text_t = dom.Text()
        text_t.data = str_tiles

        sp_tag.appendChild(text_sp)
        tile_tag.appendChild(text_t)
        maptag.appendChild(sp_tag)
        maptag.appendChild(tile_tag)

        with open(dest, 'w') as xml_file:
            doc.writexml(xml_file)

if __name__ == '__main__':
    main()
