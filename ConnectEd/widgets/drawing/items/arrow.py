__all__ = ["BlockPin", "cmdPlaceBlockPin"]

from typing import Self, Optional

from PyQt6.QtCore    import QPointF, QRectF
from PyQt6.QtWidgets import QWidget, QStyleOptionGraphicsItem, QGraphicsItem
from PyQt6.QtGui     import QPainter, QPainterPath

from . import SignalDirection, \
              ElementBoundShapeMixin, \
              ElementChangeMixin, \
              ElementLineMixin, \
              ElementFillMixin, \
              ElementMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .port_pin import Port, BasePin


class SignalArrow(
    ElementBoundShapeMixin,
    ElementChangeMixin,
    ElementLineMixin,
    ElementFillMixin,
    QGraphicsItem
):
    _SIZE         = 8
    _S            = _SIZE
    _H            = _SIZE/2
    _PATH_AWAY    = [(-_S,0), (-_H,-_H), (0,-_H), (0,_H), (-_H,_H)]
    _PATH_TOWARDS = [(0,0), (-_H,-_H), (-_S,-_H), (-_S,_H), (-_H,_H)]
    _PATH_IN      = None # subclass to override
    _PATH_OUT     = None # subclass to override
    _PATH_BI      = [(0,0), (-_H,-_H), (-_S,0), (-_H,_H)]

    _path_in  : QPainterPath # path when in
    _path_out : QPainterPath # path when out
    _path_bi  : QPainterPath # path when bi
    _path     : QPainterPath # current path

    def __init__(
        self    : Self,
        parent  : "BasePin | Port"
    ) -> None:
        QGraphicsItem.__init__(self, parent)
        self.initBoundShape()
        self.initLine(self)
        self.initFill(self)
        self._path_in = self._buildPath(self._PATH_IN)
        self._path_out = self._buildPath(self._PATH_OUT)
        self._path_bi = self._buildPath(self._PATH_BI)
        self.onAppearanceChange()

    def onAppearanceChange(self : Self) -> None:
        """Adjust bounding rect and hit detect shape after appearance change."""
        self.prepareGeometryChange()
        w = self.line.pen.width()
        hw = w * 2 # TODO investigate clipping, this shouldn't be needed
        s = self._SIZE
        self._brect.setRect(-(s+(hw/2)), -(s+w)/2, s+hw, s+w)
        self._hshape.clear()
        self._hshape.addRect(self._brect)

    def setDirection(self : Self, direction : SignalDirection) -> None:
        match direction:
            case SignalDirection.IN:
                self._path = self._path_in
            case SignalDirection.OUT:
                self._path = self._path_out
            case _:
                self._path = self._path_bi

    def _buildPath(self : Self, points : list[tuple[int, int]]) -> QPainterPath:
        p = QPainterPath()
        p.moveTo(QPointF(*points[0]))
        for point in points[1:]:
            p.lineTo(QPointF(*point))
        p.closeSubpath()

    def paint(
        self    : Self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : Optional[QWidget] = None
    ) -> None:
        painter.setPen(self.line.pen)
        painter.setBrush(self.fill.brush)
        painter.drawPath(self._path)
