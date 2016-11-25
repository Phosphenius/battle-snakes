# -*- coding: utf-8 -*-

from abc import abstractmethod
from itertools import count

from fsm import State, FiniteStateMachine
from gui import (Button, label, StackPanel, TextDisplay,
                 StandaloneContainer, PlayerSlot)
from settings import SCR_W, ID_TO_COLOR
from colors import WHITE, DARK_GREEN
from modes import ClassicSnakeGameMode


SP_GAME_MODES_DESC = {0: 'This is the classic Snake mode',
                      1: '''Free for all mode.
Fight against bots, collect powerups and food.''',
                      2: '''Collect as much food as possible before
time runs out!''',
                      3: 'Return to main menu'}


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


class PlayingState(GameStateScreen):
    def __init__(self, game, mode):
        GameStateScreen.__init__(self, game)
        self.mode = mode
        self.game.tilemap = mode.tilemap
        self.mode.start()

    def update(self, delta_time):
        self.mode.update(delta_time)

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
                                   action=self.entry_sp_action)
        btn_multiplayer = Button(game,
                                 text='Multiplayer',
                                 action=self.entry_mp_action,
                                 enabled=False)
        btn_settings = Button(game,
                              text='Settings',
                              action=self.entry_st_action,
                              enabled=False)
        btn_credits = Button(game,
                             text='Credits',
                             action=self.entry_cr_action)
        btn_quit = Button(game,
                          text='Quit',
                          action=self.entry_qt_action)

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

    def entry_sp_action(self):
        new_state = SinglePlayerSelectModeScreen(self.game)
        self.game.curr_state.change_state(new_state)

    def entry_mp_action(self):
        pass

    def entry_st_action(self):
        self.game.curr_state.change_state(SettingsScreen(self.game))

    def entry_cr_action(self):
        self.game.curr_state.change_state(CreditsScreen(self.game))

    def entry_qt_action(self):
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
                             action=self.entry_cl_action,
                             enabled=False)
        btn_ffa = Button(game,
                         text='Free for all',
                         action=self.entry_ffa_action)
        btn_timelimit = Button(game,
                               text='Time limit',
                               action=self.entry_tl_action,
                               enabled=False)
        btn_back = Button(game,
                          text='Back',
                          action=self.entry_bk_action)

        self.stackpanel.add_widgets(btn_classic,
                                    btn_ffa,
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

    def entry_cl_action(self):
        pass

    def entry_ffa_action(self):
        state = SelectPlayerScreen(self.game, 1)
        self.game.curr_state.change_state(state)

    def entry_tl_action(self):
        pass

    def entry_bk_action(self):
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
                              action=self.entry_cl_action)
        btn_sound = Button(game,
                           text='Sound',
                           action=self.entry_sn_action)
        btn_back = Button(game,
                          text='Back',
                          action=self.entry_bk_action)

        self.stackpanel.add_widgets(btn_controls,
                                    btn_sound,
                                    btn_back)

    def entry_cl_action(self):
        pass

    def entry_sn_action(self):
        pass

    def entry_bk_action(self):
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
                               action=self.entry_bk_action)
        self.container = StandaloneContainer(game,
                                             (0, 0),
                                             150,
                                             50,
                                             self.btn_back,
                                             focus=True)

    def entry_bk_action(self):
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
        btn_no = Button(game, text='No', action=self.entry_no_action)

        self.stackpanel.add_widgets(txt_question, btn_yes, btn_no)

        self.prev_screen = None

    def entry_no_action(self):
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
