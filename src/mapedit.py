#!/usr/bin/python
# -*- coding: utf-8 -*-

import Tkinter as tk
import tkMessageBox as msgbox
import os
from collections import deque
from copy import copy

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

INIT_STATE_NAME = 'init'
EDIT_STATE_NAME = 'edit'

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

class InputManager(object):
    def __init__(self, init_mouse_x=0, init_mouse_y=0):
        self.mouse_x = init_mouse_x
        self.mouse_y = init_mouse_y
        self.curr_key_state = []
        self.prev_key_state = []
        self.curr_button_state = []
        self.prev_button_state = []

    def capture_key_press(self, event):
        self.prev_key_state = copy(self.curr_key_state)

        if event.keysym not in self.curr_key_state:
            if event.keysym == 'Meta_L':
                self.curr_key_state.append('ALT_L')
            elif event.keysym == 'Meta_R':
                self.curr_key_state.append('ALT_R')
            else:
                self.curr_key_state.append(event.keysym.upper())

    def capture_key_release(self, event):
        self.prev_key_state = copy(self.curr_key_state)

        if event.keysym == 'Meta_L':
            self.curr_key_state.remove('ALT_L')
        elif event.keysym == 'Meta_R':
            self.curr_key_state.remove('ALT_R')
        else:
            self.curr_key_state.remove(event.keysym.upper())

    def capture_button_press(self, event):
        if event.num not in self.curr_button_state:
            self.curr_button_state.append(event.num)

    def capture_button_release(self, event):
        self.prev_button_state = copy(self.curr_button_state)
        self.curr_button_state.remove(event.num)

    def mouse_motion(self, event):
        self.mouse_x = event.x
        self.mouse_y = event.y

    def update(self):
        self.prev_key_state = []
        self.prev_button_state = []

    def key_pressed(self, key):
        return key in self.curr_key_state

    def key_tapped(self, key):
        return (key not in self.curr_key_state and
                key in self.prev_key_state)

    def button_pressed(self, button):
        return button in self.curr_button_state

    def button_tapped(self, button):
        return (button not in self.curr_button_state and
                button in self.prev_button_state)

class InitState(object):
    def __init__(self, state_context):
        self.context = state_context

    def get_name(self):
        return INIT_STATE_NAME

    def enter(self):
        pass

    def leave(self):
        pass

    def update(self):
        pass

    def draw(self, screen):
        pass

class EditState(object):
    def __init__(self, state_context):
        self.context = state_context
        self.cmd_manager = CommandManager()

        self.show_grid = True
        self.show_help_lines = True

        self.point1 = None
        self.tile_line = None
        self.selected = None

        self.tiles = []
        self.wall_tex = pygame.image.load('../gfx/wall.png').convert()

    def file_save(self):
        pass

    def file_save_as(self):
        pass

    def file_close(self):
        pass

    def get_name(self):
        return EDIT_STATE_NAME

    def enter(self):
        self.context.file_menu.entryconfig(3, state=tk.NORMAL,
            command=self.file_save)
        self.context.file_menu.entryconfig(4, state=tk.NORMAL,
            command=self.file_save_as)
        self.context.file_menu.entryconfig(6, state=tk.NORMAL,
            command=self.file_close)

    def leave(self):
        self.context.file_menu.entryconfig(3, state=tk.DISABLED,
            command=None)
        self.context.file_menu.entryconfig(4, state=tk.DISABLED,
            command=None)
        self.context.file_menu.entryconfig(6, state=tk.NORMAL,
            command=None)

    def update(self):
        if self.context.input.key_pressed('CONTROL_L'):
            if self.context.input.key_tapped('Z'):
                self.cmd_manager.undo()
            elif self.context.input.key_tapped('Y'):
                self.cmd_manager.redo()

            if self.context.input.key_tapped('G'):
                self.show_grid = not self.show_grid

            if self.context.input.key_tapped('H'):
                self.show_help_lines = not self.show_help_lines

            if self.context.input.button_tapped(LEFT_MOUSE_BUTTON):
                self.fill_horizontal()
            elif self.context.input.button_tapped(RIGHT_MOUSE_BUTTON):
                self.remove_horizontal()

            if (self.context.input.button_tapped(LEFT_MOUSE_BUTTON) and
                    self.context.input.key_pressed('SHIFT_L')):
                self.fill_vertical()
            elif (self.context.input.button_tapped(RIGHT_MOUSE_BUTTON)
                  and self.context.input.key_pressed('SHIFT_L')):
                self.remove_vertical()

        self.selected = (
            (self.context.input.mouse_x / CELL_SIZE) * CELL_SIZE,
            (self.context.input.mouse_y / CELL_SIZE) * CELL_SIZE)

        if (self.context.input.button_pressed(LEFT_MOUSE_BUTTON) and
                self.selected not in self.tiles and not
                self.context.input.key_pressed('SHIFT_L')):
            cmd = ChangeTilesCommand([self.selected], self.tiles)
            self.cmd_manager.exec_cmd(cmd)

        if (self.context.input.button_tapped(LEFT_MOUSE_BUTTON) and
                self.context.input.key_pressed('SHIFT_L')):
            if self.point1 is not None:
                if (self.point1[0] == self.selected[0] or
                    self.point1[1] == self.selected[1]):

                    tile_lst = make_line_of_tiles(self.point1,
                    self.selected)

                    cmd = ChangeTilesCommand(tile_lst, self.tiles)
                    self.cmd_manager.exec_cmd(cmd)
            self.point1 = self.selected

        if self.context.input.key_tapped('SHIFT_L'):
            self.point1 = None

        if (self.context.input.button_pressed(RIGHT_MOUSE_BUTTON) and
                self.selected in self.tiles):
            cmd = ChangeTilesCommand([self.selected], self.tiles,
                remove=True)
            self.cmd_manager.exec_cmd(cmd)

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

    def draw(self, screen):
        if self.show_grid:
            self.draw_grid(screen)

        for tile in self.tiles:
            screen.blit(self.wall_tex, tile)

        pygame.draw.rect(screen, ORANGE,
            pygame.Rect(self.selected,
            (CELL_SIZE, CELL_SIZE)))

        if self.tile_line is not None:
            for tile in self.tile_line:
                screen.blit(self.wall_tex, tile)

        if self.point1 is not None:
            screen.blit(self.wall_tex, self.point1)

        if self.show_help_lines:
            half_size = CELL_SIZE / 2

            pygame.draw.line(screen, GREEN,
            (self.selected[0] + half_size, 0),
            (self.selected[0] + half_size, DISPLAY_HEIGHT))

            pygame.draw.line(screen, GREEN,
            (0, self.selected[1] + half_size),
            (DISPLAY_WIDTH, self.selected[1] + half_size))

    def draw_grid(self, screen):
        for xpos in range(0, DISPLAY_WIDTH, CELL_SIZE):
            pygame.draw.line(screen, DARK_GRAY, (xpos, 0),
                (xpos, DISPLAY_HEIGHT))

        for ypos in range(0, DISPLAY_HEIGHT, CELL_SIZE):
            pygame.draw.line(screen, DARK_GRAY, (0, ypos),
                (DISPLAY_WIDTH, ypos))

    def fill_horizontal(self):
        tile_lst = make_line_of_tiles((0, self.selected[1]),
        (DISPLAY_WIDTH, self.selected[1]))

        self.cmd_manager.exec_cmd(ChangeTilesCommand(tile_lst,
            self.tiles))

    def fill_vertical(self):
        tile_lst = make_line_of_tiles((self.selected[0], 0),
        (self.selected[0], DISPLAY_HEIGHT))

        self.cmd_manager.exec_cmd(ChangeTilesCommand(tile_lst,
            self.tiles))

    def remove_horizontal(self):
        tile_lst = make_line_of_tiles((0, self.selected[1]),
        (DISPLAY_WIDTH, self.selected[1]))

        self.cmd_manager.exec_cmd(ChangeTilesCommand(tile_lst,
            self.tiles,
        remove=True))

    def remove_vertical(self):
        tile_lst = make_line_of_tiles((self.selected[0], 0),
        (self.selected[0], DISPLAY_HEIGHT))

        self.cmd_manager.exec_cmd(ChangeTilesCommand(tile_lst,
            self.tiles, remove=True))

class MapEditor(object):
    def __init__(self):
        self.input = InputManager(DISPLAY_WIDTH * 0.5,
                                  DISPLAY_HEIGHT * 0.5)

        self.root = tk.Tk()
        self.root.bind('<Motion>', self.input.mouse_motion)
        self.root.bind('<KeyPress>', self.input.capture_key_press)
        self.root.bind('<KeyRelease>', self.input.capture_key_release)
        self.root.bind('<ButtonPress>', self.input.capture_button_press)
        self.root.bind('<ButtonRelease>',
            self.input.capture_button_release)

        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        top = self.root.winfo_toplevel()
        self.menu_bar = tk.Menu(top)
        top['menu'] = self.menu_bar
        self.file_menu = tk.Menu(self.menu_bar, tearoff=False)
        self.menu_bar.add_cascade(label='File', menu=self.file_menu,
            underline=0)

        self.file_menu.add_command(
            label='New',
            command=self.file_new,
            underline=0,
            accelerator='Ctrl+N')

        self.file_menu.add_command(
            label='Open',
            command=None,
            underline=0,
            accelerator='Ctrl+O')

        self.file_menu.add_separator()

        self.file_menu.add_command(
            label='Save',
            underline=0,
            accelerator='Ctrl+S')

        self.file_menu.add_command(label='Save As', underline=5)
        self.file_menu.add_separator()

        self.file_menu.add_command(
            label='Close',
            underline=0,
            accelerator='Ctrl+W')

        self.file_menu.add_separator()

        self.file_menu.add_command(
            label='Quit',
            command=self.exit_cmd,
            underline=0,
            accelerator='Ctrl+Q')

        self.file_menu.entryconfig(3, state=tk.DISABLED)
        self.file_menu.entryconfig(4, state=tk.DISABLED)
        self.file_menu.entryconfig(6, state=tk.DISABLED)

        self.embed = tk.Frame(self.root, width=1400, height=700)
        self.embed.grid(row=0, column=0)

        os.environ['SDL_WINDOWID'] = str(self.embed.winfo_id())

        self.root.update()
        self.fps_clock = pygame.time.Clock()
        pygame.init()
        self.screen = pygame.display.set_mode((DISPLAY_WIDTH,
                DISPLAY_HEIGHT))

        self.quit = False

        self.curr_state = InitState(self)
        self.curr_state.enter()

    def change_state(self, new_state):
        self.curr_state.leave()
        self.curr_state = new_state
        self.curr_state.enter()

    def file_new(self):
        self.change_state(EditState(self))

    def file_open(self):
        pass

    def update(self):
        self.curr_state.update()

        # Must be called at the very end of update!
        self.input.update()

    def draw(self):
        self.curr_state.draw(self.screen)

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
