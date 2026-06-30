from typing import Self

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QGraphicsItem

from .....core.check import checked

class ItemMoveMixin:
    """Methods to support moving items."""

    @checked
    def moveSave(self : Self) -> QPointF:
        if not isinstance(self, QGraphicsItem):
            raise TypeError("Bad host")
        return self.scenePos()

    @checked
    def moveRestore(self : Self, state : QPointF) -> None:
        """Restore a saved scene position (from moveSave)."""
        if not isinstance(self, QGraphicsItem):
            raise TypeError("Bad host")
        self.moveBy(
            state.x() - self.scenePos().x(), state.y() - self.scenePos().y()
        )
