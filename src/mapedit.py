#!/usr/bin/python
# -*- coding: utf-8 -*-

import Tkinter as tk
import os
from collections import deque

import pygame

from colors import BLACK, ORANGE, GREEN, DARK_GRAY


FPS = 30

CELL_SIZE = 10
ROWS = 64
COLS = 128
DISPLAY_WIDTH = COLS * CELL_SIZE
DISPLAY_HEIGHT = ROWS * CELL_SIZE

LEFT_MOUSE_BUTTON = 1
RIGHT_MOUSE_BUTTON = 3

MAX_UNDO_REDO = 1024


def make_line_of_tiles(point1, point2):
    tile_lst = []
    if point1[0] == point2[0]:
        startpoint = min(point1[1], point2[1])
        endpoint = max(point1[1], point2[1])
        for ypos in range(startpoint, endpoint+1, CELL_SIZE):
            tile_lst.append((point1[0], ypos))
    else:
        startpoint = min(point1[0], point2[0])
        endpoint = max(point1[0], point2[0])
        for xpos in range(startpoint, endpoint+1, CELL_SIZE):
            tile_lst.append((xpos, point1[1]))

    return tile_lst


class CommandManager(object):
    def __init__(self):
        self.undo_stack = deque(maxlen=MAX_UNDO_REDO)
        self.redo_stack = deque(maxlen=MAX_UNDO_REDO)

    def exec_cmd(self, cmd):
        cmd.do()

        if hasattr(cmd, 'undo'):
            self.undo_stack.append(cmd)

    def undo(self):
        if len(self.undo_stack) > 0:
            cmd = self.undo_stack.pop()
            self.redo_stack.append(cmd)
            cmd.undo()

    def redo(self):
        if len(self.redo_stack) > 0:
            cmd = self.redo_stack.pop()
            self.undo_stack.append(cmd)
            cmd.do()


class ChangeTilesCommand(object):
    def __init__(self, tiles, tilemap, remove=False):
        self.tile_lst = tiles
        self.tilemap = tilemap
        self.tiles_changed = []
        self.remove = remove

    def do(self):
        for tile in self.tile_lst:
            if self.remove:
                if tile in self.tilemap:
                    self.tilemap.remove(tile)
                    self.tiles_changed.append(tile)
            else:
                if tile not in self.tilemap:
                    self.tilemap.append(tile)
                    self.tiles_changed.append(tile)

    def undo(self):
        for tile in self.tiles_changed:
            if self.remove:
                if tile not in self.tilemap:
                    self.tilemap.append(tile)
            else:
                if tile in self.tilemap:
                    self.tilemap.remove(tile)


class MapEditor(object):
    def __init__(self):
        self.cmd_manager = CommandManager()

        self.root = tk.Tk()
        self.root.bind('<Motion>', self.motion)
        self.root.bind('<ButtonPress>', self.on_button_press)
        self.root.bind('<ButtonRelease>', self.on_button_release)
        self.root.bind('<Control-g>', self.toggle_grid)
        self.root.bind('<Control-h>', self.toggle_helper_lines)
        self.root.bind('<KeyPress>', self.on_key_press)
        self.root.bind('<Shift-KeyRelease>', self.shift_release)
        self.root.bind('<Control-z>', self.on_undo)
        self.root.bind('<Control-y>', self.on_redo)
        self.root.bind('<Control-Button-1>', self.fill_horizontal)
        self.root.bind('<Control-Alt-Button-1>', self.fill_vertical)
        self.root.bind('<Control-Button-3>', self.remove_horizontal)
        self.root.bind('<Control-Alt-Button-3>', self.remove_vertical)

        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        top = self.root.winfo_toplevel()
        self.menu_bar = tk.Menu(top)
        top['menu'] = self.menu_bar
        self.file_menu = tk.Menu(self.menu_bar)
        self.menu_bar.add_cascade(label='File', menu=self.file_menu)
        self.file_menu.add_command(label='new')
        self.file_menu.add_command(label='open')
        self.file_menu.add_command(label='save')
        self.file_menu.add_command(label='save as')
        self.file_menu.add_command(label='exit',
            command=self.exit_cmd)

        self.edit_menu = tk.Menu(self.menu_bar)
        self.menu_bar.add_cascade(label='Edit', menu=self.edit_menu)
        self.edit_menu.add_command(label='Undo',
            command=self.cmd_manager.undo)
        self.edit_menu.add_command(label='Redo',
            command=self.cmd_manager.redo)

        self.embed = tk.Frame(self.root, width=1400, height=700)
        self.embed.grid(row=0, column=0)

        os.environ['SDL_WINDOWID'] = str(self.embed.winfo_id())

        self.root.update()
        self.fps_clock = pygame.time.Clock()
        pygame.init()
        self.screen = pygame.display.set_mode((DISPLAY_WIDTH,
                DISPLAY_HEIGHT))

        self.quit = False

        self.selected = None
        self.mouse_x = 0
        self.mouse_y = 0

        self.wall_tex = pygame.image.load('../gfx/wall.png').convert()
        self.tiles = []

        self.show_grid = True
        self.show_helper_lines = True

        self.shift_pressed = False
        self.point1 = None

        self.tile_line = None

        self.mouse_state = {LEFT_MOUSE_BUTTON:0, RIGHT_MOUSE_BUTTON:0}

    def on_undo(self, _):
        self.cmd_manager.undo()

    def on_redo(self, _):
        self.cmd_manager.redo()

    def fill_horizontal(self, _):
        tile_lst = make_line_of_tiles((0, self.selected[1]),
        (DISPLAY_WIDTH, self.selected[1]))

        self.cmd_manager.exec_cmd(ChangeTilesCommand(tile_lst,
            self.tiles))

    def fill_vertical(self, _):
        tile_lst = make_line_of_tiles((self.selected[0], 0),
        (self.selected[0], DISPLAY_HEIGHT))

        self.cmd_manager.exec_cmd(ChangeTilesCommand(tile_lst,
            self.tiles))

    def remove_horizontal(self, _):
        tile_lst = make_line_of_tiles((0, self.selected[1]),
        (DISPLAY_WIDTH, self.selected[1]))

        self.cmd_manager.exec_cmd(ChangeTilesCommand(tile_lst,
            self.tiles,
        remove=True))

    def remove_vertical(self, _):
        tile_lst = make_line_of_tiles((self.selected[0], 0),
        (self.selected[0], DISPLAY_HEIGHT))

        self.cmd_manager.exec_cmd(ChangeTilesCommand(tile_lst,
            self.tiles, remove=True))

    def on_key_press(self, event):
        if event.keysym == 'Shift_L':
            self.shift_pressed = True

    def shift_release(self, _):
        self.shift_pressed = False
        self.point1 = None

    def motion(self, event):
        self.mouse_x = event.x
        self.mouse_y = event.y

    def on_button_press(self, event):
        self.mouse_state[event.num] = True

    def on_button_release(self, event):
        self.mouse_state[event.num] = False

        if event.num == LEFT_MOUSE_BUTTON and self.shift_pressed:
            if self.point1 is not None:
                if (self.point1[0] == self.selected[0] or
                    self.point1[1] == self.selected[1]):

                    tile_lst = make_line_of_tiles(self.point1,
                    self.selected)

                    self.cmd_manager.exec_cmd(ChangeTilesCommand(tile_lst,
                        self.tiles))

                    self.point1 = self.selected
            else:
                self.point1 = self.selected

    def toggle_grid(self, _):
        self.show_grid = not self.show_grid

    def toggle_helper_lines(self, _):
        self.show_helper_lines = not self.show_helper_lines

    def update(self):
        self.selected = ((self.mouse_x / CELL_SIZE) * CELL_SIZE,
            (self.mouse_y / CELL_SIZE) * CELL_SIZE)

        if (self.mouse_state[LEFT_MOUSE_BUTTON] and
        self.selected not in self.tiles) and not self.shift_pressed:
            self.cmd_manager.exec_cmd(ChangeTilesCommand([self.selected],
                self.tiles))

        if (self.mouse_state[RIGHT_MOUSE_BUTTON] and
        self.selected in self.tiles):
            self.cmd_manager.exec_cmd(ChangeTilesCommand([self.selected],
                self.tiles, remove=True))

        if self.point1 is not None:
            if self.point1[0] == self.selected[0]:
                self.tile_line = make_line_of_tiles(self.point1,
                self.selected)
            elif self.point1[1] == self.selected[1]:
                self.tile_line = make_line_of_tiles(self.point1,
                self.selected)
            else:
                self.tile_line = None
        else:
            self.tile_line = None

    def draw_grid(self):
        for xpos in range(0, DISPLAY_WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, DARK_GRAY, (xpos, 0),
                (xpos, DISPLAY_HEIGHT))

        for ypos in range(0, DISPLAY_HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, DARK_GRAY, (0, ypos),
                (DISPLAY_WIDTH, ypos))

    def draw(self):
        if self.show_grid:
            self.draw_grid()

        for tile in self.tiles:
            self.screen.blit(self.wall_tex, tile)

        pygame.draw.rect(self.screen, ORANGE,
            pygame.Rect(self.selected,
            (CELL_SIZE, CELL_SIZE)))

        if self.tile_line is not None:
            for tile in self.tile_line:
                self.screen.blit(self.wall_tex, tile)

        if self.point1 is not None:
            self.screen.blit(self.wall_tex, self.point1)

        if self.show_helper_lines:
            half_size = CELL_SIZE / 2

            pygame.draw.line(self.screen, GREEN,
            (self.selected[0] + half_size, 0),
            (self.selected[0] + half_size, DISPLAY_HEIGHT))

            pygame.draw.line(self.screen, GREEN,
            (0, self.selected[1] + half_size),
            (DISPLAY_WIDTH, self.selected[1] + half_size))

    def run(self):
        while not self.quit:
            for _ in pygame.event.get():
                pass

            self.screen.fill(BLACK)
            self.fps_clock.tick(FPS)
            self.update()
            self.draw()
            pygame.display.flip()
            self.root.update()

    def exit_cmd(self):
        self.quit = True


def main():
    mapedit = MapEditor()
    mapedit.run()

if __name__ == '__main__':
    main()
