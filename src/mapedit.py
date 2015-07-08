#!/usr/bin/python
# -*- coding: utf-8 -*-

import Tkinter as tk
import os

import pygame

from colors import BLACK, ORANGE, DARK_GRAY


FPS = 30

CELL_SIZE = 10
ROWS = 64
COLS = 128
DISPLAY_WIDTH = COLS * CELL_SIZE
DISPLAY_HEIGHT = ROWS * CELL_SIZE

LEFT_MOUSE_BUTTON = 1
RIGHT_MOUSE_BUTTON = 3


class MapEditor(object):
    def __init__(self):
        self.root = tk.Tk()
        self.root.bind('<Motion>', self.motion)
        self.root.bind('<ButtonPress>', self.on_button_press)
        self.root.bind('<ButtonRelease>', self.on_button_release)
        self.root.bind('<Control-g>', self.toggle_grid)
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        top = self.root.winfo_toplevel()
        self.menuBar = tk.Menu(top)
        top['menu'] = self.menuBar
        self.file_menu = tk.Menu(self.menuBar)
        self.menuBar.add_cascade(label='File', menu=self.file_menu)
        self.file_menu.add_command(label='new')
        self.file_menu.add_command(label='open')
        self.file_menu.add_command(label='save')
        self.file_menu.add_command(label='save as')
        self.file_menu.add_command(label='exit', 
            command=self.__exitHandler)

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
        
        self.mouse_state = {LEFT_MOUSE_BUTTON:0, RIGHT_MOUSE_BUTTON:0}

    def motion(self, event):
        self.mouse_x = event.x 
        self.mouse_y = event.y 
    
    def on_button_press(self, event):
        self.mouse_state[event.num] = True
    
    def on_button_release(self, event):  
        self.mouse_state[event.num] = False
            
    def toggle_grid(self, event):
        self.show_grid = not self.show_grid
            
    def update(self, delta_time):
        if (self.mouse_state[LEFT_MOUSE_BUTTON] and 
        self.selected not in self.tiles):
            self.tiles.append(self.selected)
            
        if (self.mouse_state[RIGHT_MOUSE_BUTTON] and
        self.selected in self.tiles):
            self.tiles.remove(self.selected)
            
        self.selected = ((self.mouse_x / CELL_SIZE) * CELL_SIZE, 
            (self.mouse_y / CELL_SIZE) * CELL_SIZE)

    def draw_grid(self):
        for xpos in range(0, DISPLAY_WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, DARK_GRAY, (xpos, 0), 
                (xpos, DISPLAY_HEIGHT))

        for ypos in range(0, DISPLAY_HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, DARK_GRAY, (0, ypos),
                (DISPLAY_WIDTH, ypos))

    def draw(self, delta_time):
        if self.show_grid:
            self.draw_grid()
            
        for tile in self.tiles:
            self.screen.blit(self.wall_tex, tile)
            
        pygame.draw.rect(self.screen, ORANGE, 
            pygame.Rect(self.selected, 
            (CELL_SIZE, CELL_SIZE)))

    def run(self):
        while not self.quit:
            for event in pygame.event.get():
                pass
                
            self.screen.fill(BLACK)
            delta_time = (self.fps_clock.tick(FPS) / 1000.0)
            self.update(delta_time)
            self.draw(delta_time)
            pygame.display.flip()
            self.root.update()

    def __exitHandler(self):
        self.quit = True


def main():
    mapedit = MapEditor()
    mapedit.run()

if __name__ == '__main__':
    main()
