__all__ = ["BlockPin", "cmdPlaceBlockPin"]

from typing import Self, Optional

from PyQt6.QtCore    import QRectF
from PyQt6.QtWidgets import QWidget, QStyleOptionGraphicsItem, QGraphicsItem
from PyQt6.QtGui     import QPainter, QPainterPath

from . import ElementLineMixin, ElementFillMixin, ElementMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .port_pin import BasePin

class Node(
    ElementLineMixin,
    ElementFillMixin,
    ElementMixin,
    QGraphicsItem
):
    # class attributes
    _SIZE = 4

    # instance attributes
    _rect      : QRectF
    _shape     : QPainterPath
    _path_open : QPainterPath
    _path_nc   : QPainterPath

    def __init__(
        self   : Self,
        parent : "BasePin"
    ) -> None:
        QGraphicsItem.__init__(self, parent)
        ElementMixin.initElement(self)
        self._rect = QRectF()
        self._shape = QPainterPath()
        s = self._SIZE / 2
        self._path_open = QPainterPath()
        self._path_open.addRect(QRectF(-s, -s, 2*s, 2*s))
        self._path_nc = QPainterPath()
        self._path_nc.moveTo(-s, +s)
        self._path_nc.lineTo(+s, -s)
        self._path_nc.moveTo(+s, +s)
        self._path_nc.lineTo(-s, -s)
        self.onGeometryChange()

    def onGeometryChange(self : Self) -> None:
        self.prepareGeometryChange()
        s = (self._SIZE + self.line.pen.width()) / 2
        self._rect.setRect(-s, -s, 2*s, 2*s)
        self._shape.clear()
        self._shape.addRect(self._rect)

    def boundingRect(self : Self) -> QRectF:
        return self._rect

    def shape(self : Self) -> QPainterPath:
        return self._shape

    def paint(
        self    : Self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : Optional[QWidget] = None
    ) -> None:
        painter.setPen(self.line.pen)
        painter.setBrush(self.fill.brush)
        painter.drawPath(self._path_open)
