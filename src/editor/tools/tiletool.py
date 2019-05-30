# -*- coding: utf-8 -*-

from fsm import StateMachine
from editor.tools.base import Selection, BaseToolState
import colors
import utils


class SelectState(BaseToolState):
    """
    State for selection
    """
    def __init__(self, tool):
        BaseToolState.__init__(self, tool)
        self.selection = Selection(self.tool.editor)
        self.guidelines_prev_state = None

    def enter(self):
        self.guidelines_prev_state = \
            self.tool.editor.helplines_var.get()
        self.tool.editor.helplines_var.set(0)

    def leave(self):
        self.tool.editor.helplines_var.set(self.guidelines_prev_state)

    def update(self):
        self.selection.update()

        if (self.tool.editor.input.key_pressed('CONTROL_L') and
                self.tool.editor.input.key_pressed('C')):
            self.tool.editor.clipboard = self.selection.get_tiles()

    def draw(self):
        self.selection.draw()
        self.tool.editor.draw_rect_cursor(colors.YELLOW)


class InsertState(BaseToolState):
    def draw(self):
        self.tool.editor.draw_rect_cursor(colors.GREEN)


class PasteState(BaseToolState):
    def __init__(self, tool):
        BaseToolState.__init__(tool)
        self.preview = None

    def enter(self):
        self.preview = self.tool.editor.clipboard

    def draw(self):
        if self.preview:
            tilemap = self.tool.editor.tilemap


class DeleteState(BaseToolState):
    def __init__(self, tool):
        BaseToolState.__init__(self, tool)
        self.prev_guide_line_color = None

    def enter(self):
        self.prev_guide_line_color = self.tool.editor.guide_line_color
        self.tool.editor.guide_line_color = (180, 100, 20)

    def leave(self):
        self.tool.editor.guide_line_color = self.prev_guide_line_color

    def draw(self):
        self.tool.editor.draw_rect_cursor((180, 100, 20))

class TileTool(StateMachine):
    def __init__(self, editor):
        self.editor = editor

        StateMachine.__init__(self, InsertState(self))

        self.clipboard = None

    def update(self):
        self.current_state.update()

        # FIXME: Maybe this should be inside each state?
        if self.editor.input.key_tapped('S'):
            self.change_state(SelectState(self))
        elif self.editor.input.key_tapped('T'):
            self.change_state(InsertState(self))
        elif self.editor.input.key_tapped('D'):
            self.change_state(DeleteState(self))
        elif (self.editor.input.key_tapped('CONTROL_L') and
              self.editor.input.key_tapped('V')):
            self.change_state(PasteState(self))

    def draw(self, screen):
        self.current_state.draw()
