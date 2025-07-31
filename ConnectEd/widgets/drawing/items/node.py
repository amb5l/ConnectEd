__all__ = ["BlockPin", "cmdPlaceBlockPin"]

from typing import Self, Optional

from PyQt6.QtCore    import QRectF
from PyQt6.QtWidgets import QWidget, QStyleOptionGraphicsItem, QGraphicsItem
from PyQt6.QtGui     import QPainter, QPainterPath

from . import ElementBoundShapeMixin, \
              ElementChangeMixin, \
              ElementLineMixin, \
              ElementFillMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .port_pin import BasePin


class Node(
    ElementBoundShapeMixin,
    ElementChangeMixin,
    ElementLineMixin,
    ElementFillMixin,
    QGraphicsItem
):
    # class attributes
    _SIZE = 4

    # instance attributes
    _brect     : QRectF        # bounding rect
    _hshape    : QPainterPath  # hit detect shape
    _path_open : QPainterPath  # path when open
    _path_nc   : QPainterPath  # path when closed

    def __init__(
        self   : Self,
        parent : "BasePin"
    ) -> None:
        QGraphicsItem.__init__(self, parent)
        self.initBoundShape()
        self.initLine(self)
        self.initFill(self)
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
        self._brect.setRect(-s, -s, 2*s, 2*s)
        self._hshape.clear()
        self._hshape.addRect(self._brect)

    def paint(
        self    : Self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : Optional[QWidget] = None
    ) -> None:
        painter.setPen(self.line.pen)
        painter.setBrush(self.fill.brush)
        painter.drawPath(self._path_open)
