from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor
from enum import Enum, auto


class CanvasStateMixin:
    class State(Enum):
        SELECT         = auto() # (ready to) select
        SELECT_DRAG    = auto() # selection box drag in progress
        SELECT_SLIDE   = auto() # selection slide in progress
        SELECT_MOVE    = auto() # selection move in progress
        SELECT_DUP     = auto() # selection duplication in progress
        SELECT_WIN_0   = auto() # ready to draw selection window
        SELECT_WIN_1   = auto() # selection window in progress
        ZOOM_WIN_0     = auto() # ready to draw zoom window
        ZOOM_WIN_1     = auto() # zoom window in progress
        PASTE          = auto() # ready to paste
        PLACE_BLOCK_0  = auto() # ready to place block
        PLACE_BLOCK_1  = auto() # block place in progress

    def setMode(self, mode):
        # enable/disable actions accordingly
        self.parent().menuBar.menus["Edit"][Menu.EDIT_SELECT].setEnabled(mode == self.Mode.SELECT)

    def setState(self, state):
        self.State = state
        self.status(state)
        match state:
            case self.State.IDLE:
                self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
            case _:
                self.setCursor(QCursor(Qt.CursorShape.CrossCursor))

    def status(self, mode):
        match mode:
            case self.State.IDLE:           t = "Ready"
            case self.State.SELECT:         t = "Drag to resize selection box, Release to complete selection"
            case self.State.SELECT_OR_MOVE: t = "Drag to move selection"
            case self.State.DRAG:           t = "Drag"
            case self.State.BLOCK_ADD:      t = "Click to start creating a block"
            case self.State.BLOCK_ADDING_1: t = "To create a block, either (a) drag then release, or (b) release then move then click"
            case _:                             t = "UNKNOWN EDIT MODE"
        self.win.statusBar.msg.setText(t)
        self.win.statusBar.msg.update()
