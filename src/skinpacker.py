#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
Script for packing and unpacking skin textures
"""


import argparse

from pygame import image, Surface, Rect, transform
from pygame.locals import SRCALPHA

from utils import add_vecs

HEAD = Rect(0, 0, 10, 10)
STRAIGHT1 = Rect(20, 20, 10, 10)
STRAIGHT2 = Rect(30, 20, 10, 10)
TAIL = Rect(20, 0, 10, 10)
TURN = Rect(0, 20, 10, 10)

ROT_OFFSET = {0: (0, 0), -90: (10, 0), -180: (10, 10), -270: (0, 10)}


def main():
    parser = argparse.ArgumentParser(description='Pack skin textures')
    parser.add_argument('src')
    parser.add_argument('dst')
    parser.add_argument('-u', dest='unpack', const=True,
                        type=bool, default=False, nargs="?")

    args = parser.parse_args()

    src_img = image.load(args.src)

    if args.unpack:
        dst_img = Surface((10, 50), flags=SRCALPHA)

        dst_img.blit(src_img, (0, 00), HEAD)
        dst_img.blit(src_img, (0, 10), STRAIGHT1)
        dst_img.blit(src_img, (0, 20), STRAIGHT2)
        dst_img.blit(src_img, (0, 30), TAIL)
        dst_img.blit(src_img, (0, 40), TURN)
    else:
        dst_img = Surface((40, 40), flags=SRCALPHA)

        single_tile = Surface((10, 10), flags=SRCALPHA)

        seq = ((HEAD, (0, 0)), (TAIL, (0, 30)), (TURN, (0, 40)))
        for tile, tile_pos in seq:
            single_tile.fill((0, 0, 0, 0))
            single_tile.blit(src_img, (0, 0), Rect(tile_pos, (10, 10)))

            for rot, offset in ROT_OFFSET.items():
                pos = add_vecs(tile.topleft, offset)
                dst_img.blit(transform.rotate(single_tile, rot), pos)

        for tile, tile_pos in ((STRAIGHT1, (0, 10)),
                               (STRAIGHT2, (0, 20))):
            single_tile.fill((0, 0 , 0 , 0))
            single_tile.blit(src_img, (0, 0), Rect(tile_pos, (10, 10)))

            dst_img.blit(single_tile, tile)

            pos = add_vecs(tile.topleft, (0, 10))
            dst_img.blit(transform.rotate(single_tile, -90), pos)

    image.save(dst_img, args.dst)

if __name__ == '__main__':
    main()
