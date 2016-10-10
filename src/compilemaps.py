#!/usr/bin/python2
# -*- coding: utf-8 -*-

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
from utils import vec_lst_to_str

MAP_SRC_DIR = '../data/mapsources'
MAP_DEST_DIR = '../data/maps'


def create_vec_lst_tag(tag_name, lst):
    """Creates an XML tag containing the specified vector list."""
    tag = dom.Element(tag_name)
    text = dom.Text()
    text.data = vec_lst_to_str(lst)
    tag.appendChild(text)
    return tag


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

        mapsurf = pygame.image.load(os.path.join(src, 'map.png'))
        mapdata = pygame.PixelArray(mapsurf)

        width, height = mapsurf.get_size()
        tiles = []
        spawnpoints = []

        for row in range(height):
            for col in range(width):
                if mapdata[col][row] == mapsurf.map_rgb(WHITE):
                    tiles.append((col, row))
                elif mapdata[col][row] == mapsurf.map_rgb(BLUE):
                    spawnpoints.append((col, row))

        doc = dom.parse(dest)
        maptag = doc.firstChild

        # Add 'size' attr
        size_attr = dom.Attr('size')
        size_attr.value = '{0}x{1}'.format(width, height)
        maptag.setAttributeNode(size_attr)

        maptag.appendChild(create_vec_lst_tag('Spawnpoints', spawnpoints))
        maptag.appendChild(create_vec_lst_tag('Tiles', tiles))

        with open(dest, 'w') as xml_file:
            doc.writexml(xml_file)

if __name__ == '__main__':
    main()
