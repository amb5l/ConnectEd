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
            view.action("Appearance...", view.ui.editAppearance),
            view.action("Properties...", view.ui.editProperties)
        ]
