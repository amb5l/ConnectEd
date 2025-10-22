from typing import Self

from PyQt6.QtGui     import QAction
from PyQt6.QtWidgets import QMenu

from .....app import window

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...views.drawing import DrawingView


class ElementMenuMixin:
    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        return [
            view.ctxMenuAction("Appearance...", view.ui.editAppearance),
            view.ctxMenuAction("Properties...", view.ui.editProperties)
        ]

    def ctxMenuSeparator(self : Self) -> QAction:
        action = QAction()
        action.setSeparator(True)
        return action
