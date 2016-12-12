# -*- coding: utf-8 -*-

from abc import abstractmethod
from itertools import count

from pygame.locals import K_ESCAPE

from fsm import State, FiniteStateMachine
from gui import (Button, label, StackPanel, TextDisplay,
                 StandaloneContainer, PlayerSlot)
from constants import SCR_W
from colors import WHITE, DARK_GREEN, RED, BLUE
from modes import ClassicSnakeGameMode


SP_GAME_MODES_DESC = {0: 'This is the classic Snake mode',
                      1: '''Collect as much food as possible before
time runs out!''',
                      2: 'Return to main menu'}

ID_TO_COLOR = {0: RED, 1: BLUE}


class GameStateScreen(State):
    """
    Serves as the base class for game states and screens.
    """
    def __init__(self, game):
        self.game = game

    @abstractmethod
    def update(self, delta_time):
        pass

    @abstractmethod
    def draw(self):
        pass

    def enter(self, old_state):
        pass

    def leave(self):
        pass


class InGameState(GameStateScreen, FiniteStateMachine):
    def __init__(self, game, mode):
        GameStateScreen.__init__(self, game)
        self.mode = mode
        FiniteStateMachine.__init__(self, CountdownScreen(game, mode))

    def update(self, delta_time):
        self.curr_state.update(delta_time)

    def draw(self):
        self.curr_state.draw()


class GameOverScreen(GameStateScreen):
    def __init__(self, game, mode):
        GameStateScreen.__init__(self, game)
        self.mode = mode
        self.stack_panel = StackPanel(game, (515, 400), 250)

        btn_again = Button(game, text='Play again',
                           action=self.btn_again_action)
        btn_menu = Button(game, text='Return to main menu',
                          action=self.btn_menu_action)
        btn_quit = Button(game, text='Quit',
                          action=self.btn_quit_action)

        self.stack_panel.add_widgets(btn_again, btn_menu, btn_quit)

    def btn_again_action(self):
        self.mode.reinit()
        screen = CountdownScreen(self.game, self.mode)
        self.game.curr_state.change_state(screen)

    def btn_menu_action(self):
        self.game.change_state(MenuState(self.game))

    def btn_quit_action(self):
        self.game.curr_state.change_state(QuitScreen(self.game))

    def update(self, delta_time):
        self.stack_panel.update(delta_time)

    def draw(self):
        self.stack_panel.draw()

        self.game.graphics.draw_string((600, 250), 'Game Over!',
                                       WHITE, big=True)


class GamePausedScreen(GameStateScreen):
    def __init__(self, game, mode):
        GameStateScreen.__init__(self, game)
        self.mode = mode
        self.prev_state = None

        self.stack_panel = StackPanel(game, (515, 280), 250)

        lab_paused = label(game, text='Game paused')
        btn_resume = Button(game, text='Resume Game',
                            action=self.btn_resume_action)
        btn_opts = Button(game, text='Options',
                          action=self.btn_opts_action,
                          enabled=False)
        btn_menu = Button(game, text='Return to main menu',
                          action=self.btn_menu_action)
        btn_quit = Button(game, text='Quit',
                          action=self.btn_quit_action)

        self.stack_panel.add_widgets(lab_paused, btn_resume, btn_opts,
                                     btn_menu, btn_quit)

    def btn_resume_action(self):
        self.game.curr_state.change_state(self.prev_state)

    def btn_opts_action(self):
        pass  # TODO: Yet to be implemented.

    def btn_menu_action(self):
        self.game.change_state(MenuState(self.game))

    def btn_quit_action(self):
        self.game.curr_state.change_state(QuitScreen(self.game))

    def update(self, delta_time):
        if self.game.key_manager.key_tapped(K_ESCAPE):
            self.game.curr_state.change_state(self.prev_state)

        self.stack_panel.update(delta_time)

    def draw(self):
        self.mode.draw()
        self.stack_panel.draw()

    def enter(self, old_state):
        self.prev_state = old_state


class PlayingState(GameStateScreen):
    def __init__(self, game, mode):
        GameStateScreen.__init__(self, game)
        self.mode = mode
        # FIXME: This really necessary?
        self.game.tilemap = mode.tilemap
        self.mode.start()

    def update(self, delta_time):
        self.mode.update(delta_time)

        if self.game.key_manager.key_tapped(K_ESCAPE):
            state = GamePausedScreen(self.game, self.mode)
            self.game.curr_state.change_state(state)

    def draw(self):
        self.mode.draw()


class CountdownScreen(GameStateScreen):
    """
    Screen which displays a simple countdown.
    """
    def __init__(self, game, mode):
        GameStateScreen.__init__(self, game)
        self.mode = mode
        self.countdown = 4

    def update(self, delta_time):
        self.countdown -= delta_time

        if self.countdown <= 1:
            self.game.curr_state.change_state(PlayingState(self.game,
                                                           self.mode))

    def draw(self):
        self.mode.draw()

        self.game.graphics.draw_string((600, 310),
                                       str(int(self.countdown)),
                                       WHITE, big=True)


class MenuState(GameStateScreen, FiniteStateMachine):
    def __init__(self, game):
        GameStateScreen.__init__(self, game)
        FiniteStateMachine.__init__(self, MainMenuScreen(game))

    def update(self, delta_time):
        self.curr_state.update(delta_time)

    def draw(self):
        self.curr_state.draw()


class MainMenuScreen(GameStateScreen):
    def __init__(self, game):
        GameStateScreen.__init__(self, game)
        self.stackpanel = StackPanel(game, (200, 300), 400)

        btn_single_player = Button(game,
                                   text='Single Player',
                                   action=self.btn_sp_action)
        btn_multiplayer = Button(game,
                                 text='Multiplayer',
                                 action=self.btn_mp_action,
                                 enabled=False)
        btn_settings = Button(game,
                              text='Settings',
                              action=self.btn_st_action,
                              enabled=False)
        btn_credits = Button(game,
                             text='Credits',
                             action=self.btn_cr_action)
        btn_quit = Button(game,
                          text='Quit',
                          action=self.btn_qt_action)

        self.stackpanel.add_widgets(btn_single_player,
                                    btn_multiplayer,
                                    btn_settings,
                                    btn_credits,
                                    btn_quit)

        txt = 'Welcome to Battle Snakes!'
        textbox = TextDisplay(game, text=txt, bg_color=DARK_GREEN)
        self.container = StandaloneContainer(game,
                                             (650, 300),
                                             600,
                                             300,
                                             textbox)

    def btn_sp_action(self):
        new_state = SinglePlayerSelectModeScreen(self.game)
        self.game.curr_state.change_state(new_state)

    def btn_mp_action(self):
        pass

    def btn_st_action(self):
        self.game.curr_state.change_state(SettingsScreen(self.game))

    def btn_cr_action(self):
        self.game.curr_state.change_state(CreditsScreen(self.game))

    def btn_qt_action(self):
        self.game.curr_state.change_state(QuitScreen(self.game))

    def update(self, delta_time):
        self.stackpanel.update(delta_time)

    def draw(self):
        self.container.draw()
        self.stackpanel.draw()

    def enter(self, old_state):
        self.stackpanel.change_focus(0)


class SinglePlayerSelectModeScreen(GameStateScreen):
    def __init__(self, game):
        self.game = game
        GameStateScreen.__init__(self, game)

        self.prev_screen = None

        self.stackpanel = StackPanel(game,
                                     (200, 300),
                                     400,
                                     action=self.stackpanel_action)
        btn_classic = Button(game,
                             text='Classic Snake',
                             action=self.btn_cl_action,
                             enabled=True)
        btn_timelimit = Button(game,
                               text='Time limit',
                               action=self.btn_tl_action,
                               enabled=False)
        btn_back = Button(game,
                          text='Back',
                          action=self.btn_bk_action)

        self.stackpanel.add_widgets(btn_classic,
                                    btn_timelimit,
                                    btn_back)

        self.textbox = TextDisplay(game, bg_color=DARK_GREEN)

        self.container = StandaloneContainer(game,
                                             (650, 300),
                                             600,
                                             300,
                                             self.textbox)
        self.stackpanel_action(0)

    def stackpanel_action(self, selected):
        # TODO: retrieve text only when focused
        txt = SP_GAME_MODES_DESC[selected]
        self.textbox.set_text(txt)

    def btn_cl_action(self):
        state = SelectPlayerScreen(self.game, 1)
        self.game.curr_state.change_state(state)

    def btn_tl_action(self):
        pass

    def btn_bk_action(self):
        self.game.curr_state.change_state(self.prev_screen)

    def update(self, delta_time):
        self.stackpanel.update(delta_time)

    def draw(self):
        self.container.draw()
        self.stackpanel.draw()

    def enter(self, old_state):
        self.prev_screen = old_state


class SettingsScreen(GameStateScreen):
    def __init__(self, game):
        self.game = game
        GameStateScreen.__init__(self, game)
        self.prev_screen = None
        self.stackpanel = StackPanel(game, (SCR_W / 2 - 200, 300), 400)

        btn_controls = Button(game,
                              text='Controls',
                              action=self.btn_cl_action)
        btn_sound = Button(game,
                           text='Sound',
                           action=self.btn_sn_action)
        btn_back = Button(game,
                          text='Back',
                          action=self.btn_bk_action)

        self.stackpanel.add_widgets(btn_controls,
                                    btn_sound,
                                    btn_back)

    def btn_cl_action(self):
        pass

    def btn_sn_action(self):
        pass

    def btn_bk_action(self):
        self.game.curr_state.change_state(self.prev_screen)

    def update(self, delta_time):
        self.stackpanel.update(delta_time)

    def draw(self):
        self.stackpanel.draw()

    def enter(self, old_state):
        self.prev_screen = old_state


class CreditsScreen(GameStateScreen):
    def __init__(self, game):
        self.game = game
        GameStateScreen.__init__(self, game)
        self.prev_screen = None

        self.btn_back = Button(game,
                               text='Back',
                               action=self.btn_bk_action)
        self.container = StandaloneContainer(game,
                                             (0, 0),
                                             150,
                                             50,
                                             self.btn_back,
                                             focus=True)

    def btn_bk_action(self):
        self.game.curr_state.change_state(self.prev_screen)

    def update(self, delta_time):
        self.container.update(delta_time)

    def draw(self):
        text = 'Coding and GFX: Luca Kredel'
        self.game.graphics.draw_string((300, 50), text, WHITE, big=True)
        text = 'Xolonium Font: Severin Meyer'
        self.game.graphics.draw_string((300, 70), text, WHITE, big=True)
        self.container.draw()

    def enter(self, old_state):
        self.prev_screen = old_state


class QuitScreen(GameStateScreen):
    def __init__(self, game):
        self.game = game
        GameStateScreen.__init__(self, game)
        self.stackpanel = StackPanel(game, (SCR_W / 2 - 200, 300), 400)

        txt_question = label(game,
                             text='Are you sure you want to quit?')
        btn_yes = Button(game, text='Yes', action=self.game.quit)
        btn_no = Button(game, text='No', action=self.btn_no_action)

        self.stackpanel.add_widgets(txt_question, btn_yes, btn_no)

        self.prev_screen = None

    def btn_no_action(self):
        self.game.curr_state.change_state(self.prev_screen)

    def update(self, delta_time):
        self.stackpanel.update(delta_time)

    def draw(self):
        self.stackpanel.draw()

    def enter(self, old_state):
        self.prev_screen = old_state


class SelectPlayerScreen(GameStateScreen):
    def __init__(self, game, slots):
        GameStateScreen.__init__(self, game)

        self.prev_screen = None

        if not 0 < slots < 5:
            raise ValueError('Too few or too many slots specified')

        self.slots = list()
        self.slotted = set()
        self.id_counter = count()

        for slot_index in range(slots):
            pos = (300 * slot_index + 15 * slot_index + 15, 15)
            self.slots.append(PlayerSlot(game, pos, weapons=0))

    def update(self, delta_time):
        for slot in self.slots:
            slot.update(delta_time)

        if all([slot.get_ready() for slot in self.slots]):
            players = [slot.player for slot in self.slots]
            config = {'players': players}
            state = InGameState(self.game,
                                ClassicSnakeGameMode(self.game, config))
            self.game.change_state(state)

        for player_config in self.game.h_player_configs:

            enter_key = player_config['ctrls']['action']
            back_key = player_config['ctrls']['nextweapon']

            if (self.game.key_manager.key_tapped(enter_key) and
                    player_config['hpid'] not in self.slotted):
                for slot in self.slots:

                    if slot.is_empty():
                        self.slotted.add(player_config['hpid'])
                        _id = self.id_counter.next()
                        player_config['id'] = _id
                        player_config['color'] = ID_TO_COLOR[_id]
                        slot.player = player_config
                        break

            elif self.game.key_manager.key_tapped(back_key):
                self.game.curr_state.curr_state = self.prev_screen

    def draw(self):
        for slot in self.slots:
            slot.draw()

    def enter(self, old_state):
        self.prev_screen = old_state
