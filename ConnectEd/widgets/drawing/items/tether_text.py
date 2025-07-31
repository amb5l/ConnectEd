__all__ = ["Tether","TetherText"]

from typing import Self, Optional

from PyQt6.QtCore    import QPointF, QRectF
from PyQt6.QtWidgets import QWidget, QGraphicsItem, QStyleOptionGraphicsItem, \
                            QGraphicsSceneMouseEvent
from PyQt6.QtGui     import QPainter

from . import KPLoc

from .base_text import BaseText
from .key_point import KeyPoint


class Tether(QGraphicsItem):
    """Tether line between a TetherText anchor and its parent."""

    _item  : "TetherText"
    _pos   : QPointF      # TetherText anchor position
    _ppos  : QPointF      # parent leat keypoint position in parent coords
    _brect : QRectF       # Bounding rectangle

    def __init__(self, item: "TetherText", visible : bool = False):
        super().__init__(item)  # Parent it to the TetherText
        self._item = item
        self.setZValue(-1)  # Draw behind the TetherText
        self.setVisible(visible)
        self.setFlag( self.GraphicsItemFlag.ItemIgnoresTransformations , False )
        self.onPositionChange(self._item.pos())

    def mousePressEvent(self : Self, event : QGraphicsSceneMouseEvent) -> None:
        self._item.mousePressEvent(event)

    def mouseReleaseEvent(self : Self, event : QGraphicsSceneMouseEvent) -> None:
        self._item.mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self : Self, event : QGraphicsSceneMouseEvent) -> None:
        self._item.mouseDoubleClickEvent(event)

    def onPositionChange(self : Self, pos : QPointF) -> None:
        self._brect = QRectF()
        cleat : Optional[KeyPoint] = self._item.parentItem()
        if cleat is None:
            return
        self._pos = self._item._anchor_offset
        self._ppos = cleat.scenePos() - self.scenePos()
        rect = QRectF(self._pos, self._ppos).normalized()
        self._brect = rect.adjusted(-5, -5, 5, 5) # TODO check this

    def boundingRect(self) -> QRectF:
        return self._brect

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget) -> None:
        if not self._item:
            return
        if self._brect == QRectF():
            return
        painter.setPen(self._item.outline.pen)
        painter.drawLine(self._pos, self._ppos)

class TetherText(BaseText):
    # instance variables
    _tether : Optional[Tether]

    def __init__(self : Self, bare : bool = False) -> None:
        super().__init__(bare=bare)
        self._tether = Tether(self)

    def onPositionChange(self : Self, pos : QPointF) -> None:
        self._tether.onPositionChange(pos)

    def onSelectionChange(self : Self, selected : bool) -> None:
        self._tether.setVisible(selected)
