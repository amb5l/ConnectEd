from typing import Self

from PyQt6.QtCore    import QPointF
from PyQt6.QtGui     import QAction
from PyQt6.QtWidgets import QMenu

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...views.drawing import DrawingView


class ItemMenuMixin:
    def ctxMenuItems(
        self : Self,
        view : "DrawingView",
        spos : QPointF
    ) -> list[QAction | QMenu]:
        raise NotImplementedError("Subclass must implement this method")
