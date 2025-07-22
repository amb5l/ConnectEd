__all__ = ["BlockPin", "cmdPlaceBlockPin"]

from typing import Self, Optional

from PyQt6.QtCore    import QPointF, QRectF
from PyQt6.QtWidgets import QWidget, QStyleOptionGraphicsItem
from PyQt6.QtGui     import QPainter, QPainterPath

from . import CustomGraphicsItem, ElementMixin, SignalDirection, \
              LinePref, FillPref

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .port_pin import Port, BasePin


class SignalArrow(CustomGraphicsItem, ElementMixin):
    _SIZE         = 8
    _S            = _SIZE
    _H            = _SIZE/2
    _PATH_AWAY    = [(_S,0), (_H,-_H), (0,-_H), (0,_H), (_H,_H)]
    _PATH_TOWARDS = [(0,0), (_H,-_H), (_S,-_H), (_S,_H), (_H,_H)]
    _PATH_IN      = None # subclass to override
    _PATH_OUT     = None # subclass to override
    _PATH_BI      = [(0,0), (_H,-_H), (_S,0), (_H,_H)]

    _rect     : QRectF
    _shape    : QPainterPath
    _path_in  : QPainterPath
    _path_out : QPainterPath
    _path_bi  : QPainterPath
    _path     : QPainterPath

    def __init__(
        self    : Self,
        parent  : "BasePin | Port"
    ) -> None:
        CustomGraphicsItem.__init__(self, parent)
        ElementMixin.initElement(self, line=LinePref(), fill=FillPref())
        self._rect = QRectF()
        self._shape = QPainterPath()
        self._path_in = self._buildPath(self._PATH_IN)
        self._path_out = self._buildPath(self._PATH_OUT)
        self._path_bi = self._buildPath(self._PATH_BI)
        self.onGeometryChange()

    def onGeometryChange(self : Self) -> None:
        self.prepareGeometryChange()
        w = self.appearance.line.pen.width()
        hw = w * 2 # TODO investigate clipping, this shouldn't be needed
        s = self._SIZE
        self._rect.setRect(-(hw/2), -(s+w)/2, s+hw, s+w)
        self._shape.clear()
        self._shape.addRect(self._rect)

    def _buildPath(self : Self, points : list[tuple[int, int]]) -> QPainterPath:
        p = QPainterPath()
        p.moveTo(QPointF(*points[0]))
        for point in points[1:]:
            p.lineTo(QPointF(*point))
        p.closeSubpath()
        return p

    def updateDirection(self : Self, direction : SignalDirection) -> None:
        self._direction = direction
        match direction:
            case SignalDirection.IN:
                self._path = self._path_in
            case SignalDirection.OUT:
                self._path = self._path_out
            case SignalDirection.BI:
                self._path = self._path_bi

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
        painter.setPen(self.appearance.line.pen)
        painter.setBrush(self.appearance.fill.brush)
        painter.drawPath(self._path)
