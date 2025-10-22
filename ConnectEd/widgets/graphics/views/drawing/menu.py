from typing import Self, Callable

from PyQt6.QtGui     import QAction

class DrawingViewMenuMixin:
    def ctxMenuAction(self : Self, text : str, slot : Callable):
        action = QAction(text)
        action.triggered.connect(slot)
        return action

    def ctxMenuSeparator(self : Self) -> QAction:
        action = QAction()
        action.setSeparator(True)
        return action
