# -*- coding: utf-8 -*-

import pygame

from collections import defaultdict

from powerup import PowerupManager
from core.map import TileMap
from constants import (SPAWNPOINT_TAG, WALL_TAG, PWRUP_TAG, SHOT_TAG,
                       PORTAL_TAG, SCR_W, PANEL_H)
from utils import mul_vec, add_vecs
from player import Player
import gsm


class GameModeBase(object):
    def __init__(self, game, config):
        self.game = game
        self.tilemap = TileMap(game, config['map'])
        self.pwrup_manager = PowerupManager(game)
        self.spatialhash = defaultdict(list)
        self.players = list()
        self.config = config
        self.num_dead_players = 0

        self.reinit()

    def reinit(self):
        self.pwrup_manager.clear()
        self.players = list()
        self.num_dead_players = 0
        self.build_sh()

        # TODO: Do this for bots too.
        for player_data in self.config['players']:
            player = Player(self, self.player_dead, player_data)
            self.players.append(player)

    def player_dead(self):
        self.num_dead_players += 1

        if self.num_dead_players >= len(self.players):
            screen = gsm.GameOverScreen(self.game, self)
            self.game.curr_state.change_state(screen)

    def start(self):
        for player in self.players:
            player.start()

    def update(self, delta_time):
        self.pwrup_manager.update(delta_time)
        self.game.shot_manager.update(delta_time)

        for player in self.players:
            player.update(delta_time)

        self.build_sh()
        self.handle_collisions()

    def draw(self):
        self.tilemap.draw((0, PANEL_H))

        self.pwrup_manager.draw()
        self.game.shot_manager.draw()

        pygame.draw.rect(self.game.screen, (32, 32, 32),
                         pygame.Rect(0, 0, SCR_W, PANEL_H))

        for i, player in enumerate(self.players):
            player.draw(mul_vec((290, 0), i))

    def handle_collisions(self):
        """Handle collisions."""
        for player in self.players:
            if player.snake[0] in self.tilemap.tiles:
                player.snake.take_damage(20, WALL_TAG, True, True, 1,
                                         shrink=0, slowdown=0.07)
                break

        for shot in self.game.shot_manager.shot_pool:
            if shot.pos in self.tilemap.tiles:
                shot.hit()
            if shot.pos in self.tilemap.portals:
                shot.heading = self.tilemap.portals[shot.pos][1]
                shot.pos = add_vecs(self.tilemap.portals[shot.pos][0],
                                    shot.heading)

        for entries in list(self.spatialhash.values()):
            if len(entries) > 1:
                for player in self.players:
                    for entry in entries:
                        if entry[0] == player.snake.head_tag:
                            player.coll_check_head(entries)
                        if entry[0] == player.snake.body_tag:
                            player.coll_check_body(entries)

    def build_sh(self):
        """Build spatial hash."""
        self.spatialhash.clear()

        # Add spawnpoints (So powerups don't appear on them)
        for spawnpoint in self.tilemap.spawnpoints:
            self.spatialhash[spawnpoint].append((SPAWNPOINT_TAG,
                                                 spawnpoint))

        # Add portals
        for portal_key, portal_val in list(self.tilemap.portals.items()):
            self.spatialhash[portal_key].append((PORTAL_TAG, portal_val))

        # Add powerups
        for pwrup in self.pwrup_manager.pwrup_pool:
            if pwrup.isalive:
                self.spatialhash[pwrup.pos].append((PWRUP_TAG, pwrup))

        # Add shots
        for shot in self.game.shot_manager.shot_pool:
            if shot.isalive:
                self.spatialhash[shot.pos].append((SHOT_TAG, shot))

        # Add snakes
        for player in self.players:
            self.spatialhash[player.snake[0]].append((
                player.snake.head_tag, player.snake))
            for snake in player.snake[1:]:
                self.spatialhash[snake].append((player.snake.body_tag,
                                                player.snake))


class ClassicSnakeGameMode(GameModeBase):
    def __init__(self, game, config):
        config['map'] = '../data/maps/classic_snake.xml'

        for player in config['players']:
            player['snake_config'] = {}
            player['snake_config']['hp'] = 1
            player['boost_enabled'] = False
            player['lifes'] = 0

        GameModeBase.__init__(self, game, config)

    def start(self):
        GameModeBase.start(self)
        self.pwrup_manager.spawn_pwrup('classic snake food', 1)

    def update(self, delta_time):
        GameModeBase.update(self, delta_time)

    def draw(self):
        GameModeBase.draw(self)
