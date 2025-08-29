from typing import Self, Optional

from PyQt6.QtCore    import QPointF, QRectF
from PyQt6.QtWidgets import QGraphicsPathItem, QWidget, \
                            QStyle, QStyleOptionGraphicsItem
from PyQt6.QtGui     import QPainterPath, QPainter

from . import SignalDirection, \
              ElementBoundShapeMixin, \
              ElementChangeMixin, \
              ElementLineMixin, \
              ElementFillMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .port_pin import BasePortPin, Port, BasePin


class Arrow(
    ElementBoundShapeMixin,
    ElementLineMixin,
    ElementFillMixin,
    ElementChangeMixin,
    QGraphicsPathItem
):
    _SIZE         = 8
    _S            = _SIZE
    _H            = _SIZE/2
    _PATH_AWAY    = [(_S,0), (_H,-_H), (0,-_H), (0,_H), (_H,_H)]
    _PATH_TOWARDS = [(0,0), (_H,-_H), (_S,-_H), (_S,_H), (_H,_H)]
    _PATH_BI      = [(0,0), (_H,-_H), (_S,0), (_H,_H)]
    _PATH_IN      : list[tuple[float | int, float | int]] # subclass to define
    _PATH_OUT     : list[tuple[float | int, float | int]] # subclass to define

    _path_in  : QPainterPath # path when in
    _path_out : QPainterPath # path when out
    _path_bi  : QPainterPath # path when bi

    def __init__(self : Self, parent : "BasePin | Port") -> None:
        QGraphicsPathItem.__init__(self, parent)
        f = self.GraphicsItemFlag
        self.setFlag(f.ItemIsSelectable, True)
        self.initBoundShape()
        self.initLine()
        self.initFill()
        self._path_in = self._buildPath(self._PATH_IN)
        self._path_out = self._buildPath(self._PATH_OUT)
        self._path_bi = self._buildPath(self._PATH_BI)
        self.onSettingsChange()

    def onSettingsChange(self : Self) -> None:
        s = self._SIZE + self.line.pen.width()
        self._brect = QRectF(0, -s/2, s, s)
        self._hshape.clear()
        self._hshape.addRect(self._brect)

    def onSelectionChange(self : Self, selected : bool) -> None:
        parent : BasePortPin = self.parentItem()
        parent.propagateSelection(selected, self)

    def setDirection(self : Self, direction : SignalDirection) -> None:
        match direction:
            case SignalDirection.IN:
                self.setPath(self._path_in)
            case SignalDirection.OUT:
                self.setPath(self._path_out)
            case _:
                self.setPath(self._path_bi)

    def _buildPath(self : Self, points : list[tuple[int, int]]) -> QPainterPath:
        p = QPainterPath()
        p.moveTo(QPointF(*points[0]))
        for point in points[1:]:
            p.lineTo(QPointF(*point))
        p.closeSubpath()
        return p

    def paint(
        self    : Self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : Optional[QWidget] = None
    ) -> None:
        option.state &= ~QStyle.StateFlag.State_Selected
        QGraphicsPathItem.paint(self, painter, option, widget)
