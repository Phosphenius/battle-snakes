#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Map editor using a pygame window embedded into a tkinter frame
"""

import Tkinter as tk
import tkFileDialog as filedia
import os
from collections import deque
from copy import copy
from xml.etree.ElementTree import ElementTree, Element, SubElement

import pygame

from colors import BLACK, ORANGE, GREEN, DARK_GRAY
from utils import vec_lst_to_str
from fsm import FiniteStateMachine


FPS = 30

CELL_SIZE = 10
ROWS = 64
COLS = 128
DISPLAY_WIDTH = COLS * CELL_SIZE
DISPLAY_HEIGHT = ROWS * CELL_SIZE

LEFT_MOUSE_BUTTON = 1
RIGHT_MOUSE_BUTTON = 3

MAX_UNDO_REDO = 1024

# Map object types
TILE_OBJ = 0
SPAWNPOINT_OBJ = 1


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


class TileMap(object):
    def __init__(self, tile_tex, spawnpoint_tex):
        self.tile_tex = tile_tex
        self.spawnpoint_tex = spawnpoint_tex
        self.tiles = []
        self.spawnpoints = []

    def get_free(self, obj):
        return obj not in self.tiles and obj not in self.spawnpoints

    def draw(self, screen):
        for tile in self.tiles:
            screen.blit(self.tile_tex, tile)

        for spawnpoint in self.spawnpoints:
            screen.blit(self.spawnpoint_tex, spawnpoint)

    def __getitem__(self, key):
        if key == TILE_OBJ:
            return self.tiles
        elif key == SPAWNPOINT_OBJ:
            return self.spawnpoints

    def save(self, path):
        root = Element('Map', {'description': '', 'size': '128x64'})

        portals_tag = SubElement(root, 'Portals')

        spoints = []

        for spoint in self.spawnpoints:
            spoints.append((spoint[0] / CELL_SIZE,
                            spoint[1] / CELL_SIZE))

        spawnpoints_tag = SubElement(root, 'Spawnpoints')
        spawnpoints_tag.text = vec_lst_to_str(spoints)

        tiles = []

        for tile in self.tiles:
            tiles.append((tile[0] / CELL_SIZE, tile[1] / CELL_SIZE))

        tiles_tag = SubElement(root, 'Tiles')
        tiles_tag.text = vec_lst_to_str(tiles)

        ElementTree(root).write(path)


class TileTool(object):
    def __init__(self, editor):
        self.editor = editor

        self.point1 = None
        self.tile_line = None

    def update(self):
        if self.editor.input.key_pressed('CONTROL_L'):
            if (self.editor.input.button_tapped(LEFT_MOUSE_BUTTON) and
                    self.editor.input.key_pressed('SHIFT_L')):
                self.fill_vertical()
            elif (self.editor.input.button_tapped(RIGHT_MOUSE_BUTTON)
                  and self.editor.input.key_pressed('SHIFT_L')):
                self.remove_vertical()
            elif self.editor.input.button_tapped(LEFT_MOUSE_BUTTON):
                self.fill_horizontal()
            elif self.editor.input.button_tapped(RIGHT_MOUSE_BUTTON):
                self.remove_horizontal()
        elif (self.editor.input.button_tapped(LEFT_MOUSE_BUTTON) and
              self.editor.input.key_pressed('SHIFT_L')):
            if self.point1 is not None:
                if (self.point1[0] == self.editor.selected[0] or
                        self.point1[1] == self.editor.selected[1]):

                    tile_lst = make_line_of_tiles(self.point1,
                                                  self.editor.selected)

                    cmd = EditMapCommand(
                        tile_lst,
                        self.editor.tilemap,
                        TILE_OBJ)

                    self.editor.cmd_manager.exec_cmd(cmd)
            self.point1 = self.editor.selected

        if (self.editor.input.button_pressed(LEFT_MOUSE_BUTTON) and
                self.editor.selected not in self.editor.tilemap.tiles
                and not self.editor.input.key_pressed('SHIFT_L')):

            cmd = EditMapCommand(
                [self.editor.selected],
                self.editor.tilemap,
                TILE_OBJ)

            self.editor.cmd_manager.exec_cmd(cmd)

        if self.editor.input.key_tapped('SHIFT_L'):
            self.point1 = None

        if (self.editor.input.button_pressed(RIGHT_MOUSE_BUTTON) and
                self.editor.selected in self.editor.tilemap.tiles):

            cmd = EditMapCommand(
                [self.editor.selected],
                self.editor.tilemap,
                TILE_OBJ,
                remove=True)

            self.editor.cmd_manager.exec_cmd(cmd)

        if self.point1 is not None:
            if self.point1[0] == self.editor.selected[0]:
                self.tile_line = make_line_of_tiles(self.point1,
                                                    self.editor.selected)
            elif self.point1[1] == self.editor.selected[1]:
                self.tile_line = make_line_of_tiles(self.point1,
                                                    self.editor.selected)
            else:
                self.tile_line = None
        else:
            self.tile_line = None

    def draw(self, screen):
        if self.tile_line is not None:
            for tile in self.tile_line:
                screen.blit(self.editor.wall_tex, tile)

        if self.point1 is not None:
            screen.blit(self.editor.wall_tex, self.point1)

    def fill_horizontal(self):
        tile_lst = make_line_of_tiles((0, self.editor.selected[1]),
                                      (DISPLAY_WIDTH,
                                       self.editor.selected[1]))

        cmd = EditMapCommand(tile_lst, self.editor.tilemap, TILE_OBJ)
        self.editor.cmd_manager.exec_cmd(cmd)

    def fill_vertical(self):
        tile_lst = make_line_of_tiles((self.editor.selected[0], 0),
                                      (self.editor.selected[0],
                                       DISPLAY_HEIGHT))

        cmd = EditMapCommand(tile_lst, self.editor.tilemap, TILE_OBJ)
        self.editor.cmd_manager.exec_cmd(cmd)

    def remove_horizontal(self):
        tile_lst = make_line_of_tiles((0, self.editor.selected[1]),
                                      (DISPLAY_WIDTH,
                                       self.editor.selected[1]))

        cmd = EditMapCommand(tile_lst,
                             self.editor.tilemap,
                             TILE_OBJ, remove=True)

        self.editor.cmd_manager.exec_cmd(cmd)

    def remove_vertical(self):
        tile_lst = make_line_of_tiles((self.editor.selected[0], 0),
                                      (self.editor.selected[0],
                                       DISPLAY_HEIGHT))

        cmd = EditMapCommand(tile_lst, self.editor.tilemap, TILE_OBJ,
                             remove=True)

        self.editor.cmd_manager.exec_cmd(cmd)


class SpawnpointTool(object):
    def __init__(self, editor):
        self.editor = editor

    def update(self):
        if (self.editor.input.button_pressed(LEFT_MOUSE_BUTTON) and
                self.editor.tilemap.get_free(self.editor.selected)):

            cmd = EditMapCommand(
                [self.editor.selected],
                self.editor.tilemap,
                SPAWNPOINT_OBJ)

            self.editor.cmd_manager.exec_cmd(cmd)
        elif (self.editor.input.button_pressed(RIGHT_MOUSE_BUTTON) and
              not self.editor.tilemap.get_free(self.editor.selected)):

            cmd = EditMapCommand(
                [self.editor.selected],
                self.editor.tilemap,
                SPAWNPOINT_OBJ,
                remove=True)

            self.editor.cmd_manager.exec_cmd(cmd)

    def draw(self, screen):
        pass


class CommandManager(object):

    """
    Manager for undo/redo functionality, implements the command pattern.
    """

    def __init__(self):
        self.undo_stack = deque(maxlen=MAX_UNDO_REDO)
        self.redo_stack = deque(maxlen=MAX_UNDO_REDO)

    def exec_cmd(self, cmd):
        """
        Execute a command and push it onto the undo stack.
        """
        cmd.do()

        self.undo_stack.append(cmd)

    def undo(self):
        """Undo a command."""
        if len(self.undo_stack) > 0:
            cmd = self.undo_stack.pop()
            self.redo_stack.append(cmd)
            cmd.undo()

    def redo(self):
        """Redo a command."""
        if len(self.redo_stack) > 0:
            cmd = self.redo_stack.pop()
            self.undo_stack.append(cmd)
            cmd.do()


class EditMapCommand(object):
    def __init__(self, obj_lst, tilemap, obj_type, remove=False):
        self.obj_lst = obj_lst
        self.tilemap = tilemap
        self.obj_type = obj_type
        self.objs_changed = []
        self.remove = remove

    def do(self):
        for obj in self.obj_lst:
            if self.remove:
                if obj in self.tilemap[self.obj_type]:
                    self.tilemap[self.obj_type].remove(obj)
                    self.objs_changed.append(obj)
            else:
                if self.tilemap.get_free(obj):
                    self.tilemap[self.obj_type].append(obj)
                    self.objs_changed.append(obj)

    def undo(self):
        for obj in self.objs_changed:
            if self.remove:
                if self.tilemap.get_free(obj):
                    self.tilemap[self.obj_type].append(obj)
            else:
                if obj in self.tilemap[self.obj_type]:
                    self.tilemap[self.obj_type].remove(obj)


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
        elif (event.keysym == 'Escape' and
              'CONTROL_L' in self.curr_key_state):
            self.curr_key_state.remove('CONTROL_L')
        else:
            try:
                self.curr_key_state.remove(event.keysym.upper())
            except:
                pass  # Don't do anything.

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
        self.input = self.context.input
        self.cmd_manager = CommandManager()

        self.show_grid = True
        self.show_help_lines = True

        self.selected = None

        self.wall_tex = pygame.image.load('../gfx/wall.png').convert()
        self.spawnpoint_tex = (
            pygame.image.load('../gfx/spawnpoint.png').convert())

        self.tilemap = TileMap(self.wall_tex, self.spawnpoint_tex)

        self.tool = TileTool(self)

        self.save_path = u''

    def file_save(self):
        """
        Write map data as xml to the file specified in 'save_path'.
        """
        if self.save_path is not u'':
            self.tilemap.save(self.save_path)
        else:
            self.file_save_as()

    def file_save_as(self):
        """
        Open file dialog and write map data as xml to the file
        selected by the user.
        """
        result = filedia.asksaveasfilename(
            defaultextension='.xml',
            initialdir='/',
            initialfile='untiteld',
            title='Save map')

        if result is not u'':
            self.save_path = result
            self.tilemap.save(result)

    def enter(self):
        """Enter edit state and change the file menu accordingly."""
        self.context.file_menu.entryconfig(3, state=tk.NORMAL,
                                           command=self.file_save)
        self.context.file_menu.entryconfig(4, state=tk.NORMAL,
                                           command=self.file_save_as)

    def leave(self):
        """Leave edit state and change the file menu accordingly."""
        self.context.file_menu.entryconfig(3, state=tk.DISABLED,
                                           command=None)
        self.context.file_menu.entryconfig(4, state=tk.DISABLED,
                                           command=None)

    def update(self):
        # Undo & redo
        if self.context.input.key_pressed('CONTROL_L'):
            if self.context.input.key_tapped('Z'):
                self.cmd_manager.undo()
            elif self.context.input.key_tapped('Y'):
                self.cmd_manager.redo()

            # Save file
            if self.context.input.key_tapped('S'):
                self.file_save()

            # Toggle grid
            if self.context.input.key_tapped('G'):
                self.show_grid = not self.show_grid

            # Toggle 'help lines'
            if self.context.input.key_tapped('H'):
                self.show_help_lines = not self.show_help_lines
        else:
            if self.context.input.key_tapped('T'):
                self.tool = TileTool(self)
            elif self.context.input.key_tapped('S'):
                self.tool = SpawnpointTool(self)

        # Update selected cell
        row = self.context.input.mouse_y / CELL_SIZE
        col = self.context.input.mouse_x / CELL_SIZE
        self.selected = (
            (col if col < COLS else COLS-1) * CELL_SIZE,
            (row if row < ROWS else ROWS-1) * CELL_SIZE)

        self.tool.update()

    def draw(self, screen):
        if self.show_grid:
            self.draw_grid(screen)

        self.tilemap.draw(screen)

        self.tool.draw(screen)

        pygame.draw.rect(screen, ORANGE,
                         pygame.Rect(self.selected,
                                     (CELL_SIZE, CELL_SIZE)))

        if self.show_help_lines:
            half_size = CELL_SIZE / 2

            point1 = (self.selected[0] + half_size, 0)
            point2 = (self.selected[0] + half_size, DISPLAY_HEIGHT)

            pygame.draw.line(screen, GREEN, point1, point2)

            point1 = (0, self.selected[1] + half_size)
            point2 = (DISPLAY_WIDTH, self.selected[1] + half_size)

            pygame.draw.line(screen, GREEN, point1, point2)

    def draw_grid(self, screen):
        """Draw a grid"""
        for xpos in range(0, DISPLAY_WIDTH, CELL_SIZE):
            pygame.draw.line(screen, DARK_GRAY, (xpos, 0),
                             (xpos, DISPLAY_HEIGHT))

        for ypos in range(0, DISPLAY_HEIGHT, CELL_SIZE):
            pygame.draw.line(screen, DARK_GRAY, (0, ypos),
                             (DISPLAY_WIDTH, ypos))


class MapEditor(FiniteStateMachine):
    def __init__(self):
        FiniteStateMachine.__init__(self, InitState(self))

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
            label='Quit',
            command=self.exit_cmd,
            underline=0,
            accelerator='Ctrl+Q')

        self.file_menu.entryconfig(3, state=tk.DISABLED)
        self.file_menu.entryconfig(4, state=tk.DISABLED)

        self.embed = tk.Frame(self.root, width=1400, height=700)
        self.embed.grid(row=0, column=0)

        os.environ['SDL_WINDOWID'] = str(self.embed.winfo_id())

        self.root.update()
        self.fps_clock = pygame.time.Clock()
        pygame.init()
        self.screen = pygame.display.set_mode((DISPLAY_WIDTH,
                                               DISPLAY_HEIGHT))
        self.quit = False

    def file_new(self):
        self.change_state(EditState(self))

    #~ def file_open(self):
        #~ result = filedia.askopenfilename(
            #~ defaultextension='.xml',
            #~ initialdir='/',
            #~ title='Open map')

    def update(self):
        """
        Update editor, get user input
        """
        if self.input.key_pressed('CONTROL_L'):
            if self.input.key_pressed('Q'):
                self.quit = True
            elif self.input.key_tapped('N'):
                self.file_new()
            elif self.input.key_tapped('O'):
                pass

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
