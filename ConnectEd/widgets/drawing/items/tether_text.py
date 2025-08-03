__all__ = ["Tether","TetherText"]

from typing import Self, Optional

from PyQt6.QtCore    import QPointF, QLineF
from PyQt6.QtWidgets import QGraphicsLineItem, QGraphicsSceneMouseEvent

from .base_text import BaseText
from .key_point import KeyPoint


class Tether(QGraphicsLineItem):
    """Tether line between a TetherText anchor and its parent."""

    _item  : "TetherText"
    _line  : QLineF

    def __init__(self, item: "TetherText", visible : bool = False):
        super().__init__(item)  # Parent it to the TetherText
        self._item = item
        self.setZValue(-1)  # Draw behind the TetherText
        self.setVisible(visible)
        self.setFlag( self.GraphicsItemFlag.ItemIgnoresTransformations , False )
        self._line = QLineF()
        self.setLine(self._line)
        self.onSettingsChange()
        self.onPositionChange(self._item.pos())

    def mousePressEvent(self : Self, event : QGraphicsSceneMouseEvent) -> None:
        self._item.mousePressEvent(event)

    def mouseReleaseEvent(self : Self, event : QGraphicsSceneMouseEvent) -> None:
        self._item.mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self : Self, event : QGraphicsSceneMouseEvent) -> None:
        self._item.mouseDoubleClickEvent(event)

    def onSettingsChange(self : Self) -> None:
        self.setPen(self._item.outline.pen)

    def onPositionChange(self : Self, _ : QPointF) -> None:
        cleat : Optional[KeyPoint] = self._item.parentItem()
        if cleat is None:
            return
        self._line.setP2(cleat.scenePos() - self.scenePos())
        self.setLine(self._line)

class TetherText(BaseText):
    # instance variables
    _tether : Optional[Tether]

    def __init__(self : Self, bare : bool = False) -> None:
        super().__init__(bare=bare)
        self._tether = Tether(self)

    def onSettingsChange(self : Self) -> None:
        self._tether.onSettingsChange()

    def onPositionChange(self : Self, pos : QPointF) -> None:
        self._tether.onPositionChange(pos)

    def onSelectionChange(self : Self, selected : bool) -> None:
        self._tether.setVisible(selected)

    def setAnchor(self : Self, name : str) -> None:
        super().setAnchor(name)
        self._tether.setParentItem(self._anchor)
        self._tether.onPositionChange(self.pos())
