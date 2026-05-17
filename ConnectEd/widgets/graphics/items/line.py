from typing import Self

from PyQt6.QtCore    import Qt, QPointF, QLineF
from PyQt6.QtWidgets import QGraphicsLineItem
from PyQt6.QtGui     import QPainterPath, QPainterPathStroker

from ....app import settings

from ....core.types import DataKind, LineHandleId

from ..properties import InherentProperty, PropertiesMixin

from .mixin           import ItemMixin
from .mixin.transform import ItemTransformMixin
from .mixin.shape     import ItemShapeMixin
from .mixin.paint     import ItemPaintMixin
from .mixin.handle    import ItemLineHandlesMixin
from .mixin.line      import ItemLineMixin
from .mixin.change    import ItemChangeMixin
from .mixin.clone     import ItemCloneMixin
from .mixin.xml       import ItemXmlMixin
from .mixin.menu      import ItemMenuMixin


class LineItem(
    ItemMixin,
    ItemTransformMixin,
    ItemShapeMixin,
    ItemPaintMixin,
    ItemLineHandlesMixin,
    ItemLineMixin,
    ItemChangeMixin,
    ItemCloneMixin,
    ItemXmlMixin,
    ItemMenuMixin,
    PropertiesMixin,
    QGraphicsLineItem
):
    # class attributes
    _PROPERTIES = \
        {
            "X1" : InherentProperty(
                kind   = DataKind.FLOAT,
                getter = lambda self: self.x1(),
                setter = lambda self, value: self.setX1(value)
            ),
            "Y1" : InherentProperty(
                kind   = DataKind.FLOAT,
                getter = lambda self: self.y1(),
                setter = lambda self, value: self.setY1(value)
            ),
            "X2" : InherentProperty(
                kind   = DataKind.FLOAT,
                getter = lambda self: self.x2(),
                setter = lambda self, value: self.setX2(value)
            ),
            "Y2" : InherentProperty(
                kind   = DataKind.FLOAT,
                getter = lambda self: self.y2(),
                setter = lambda self, value: self.setY2(value)
            )
        } | \
        ItemLineMixin._PROPERTIES_LINE

    # instance attributes
    _line    : QLineF

    def __init__(
        self  : Self,
        p1    : QPointF | None = None,
        p2    : QPointF | None = None,
        fresh : bool = True
    ) -> None:
        QGraphicsLineItem.__init__(self)
        self.initItem(fresh)
        p1 = p1 or QPointF()
        p2 = p2 or p1
        self._line = QLineF()
        self.setPoints(p1, p2)

    def onGeometryChange(self : Self | PropertiesMixin) -> None:
        """Allow for tolerance."""
        if not hasattr(self, "_line"):
            self._hshape = QPainterPath()
            return
        pen_width = self.pen().widthF()
        tolerance = settings().get("display/select/tolerance")
        stroke_width = pen_width + (2 * tolerance)
        line_path = QPainterPath()
        line_path.moveTo(self._line.p1())
        line_path.lineTo(self._line.p2())
        stroker = QPainterPathStroker()
        stroker.setWidth(stroke_width)
        stroker.setCapStyle(Qt.PenCapStyle.RoundCap)
        stroker.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        stroker_path = stroker.createStroke(line_path)
        self._hshape = stroker_path
        self.updateHandles()
        self.signalPropertyChanges(["X1", "Y1", "X2", "Y2"])

    def updateHandles(self : Self) -> None:
        self._handles[LineHandleId.P2].setPos(self._line.p2())

    def p1(self : Self) -> QPointF:
        return self.pos()

    def setP1(self : Self, pos : QPointF) -> None:
        self.setPoints(pos, self.p2())

    def x1(self : Self) -> float:
        return self.p1().x()

    def setX1(self : Self, value : float) -> None:
        self.setP1(QPointF(value, self.p1().y()))

    def y1(self : Self) -> float:
        return self.p1().y()

    def setY1(self : Self, value : float) -> None:
        self.setP1(QPointF(self.p1().x(), value))

    def p2(self : Self) -> QPointF:
        return self.pos() + self.line().p2()

    def setP2(self : Self, pos : QPointF) -> None:
        self.setPoints(self.p1(), pos)

    def x2(self : Self) -> float:
        return self.p2().x()

    def setX2(self : Self, value : float) -> None:
        self.setP2(QPointF(value, self.p2().y()))

    def y2(self : Self) -> float:
        return self.p2().y()

    def setY2(self : Self, value : float) -> None:
        self.setP2(QPointF(self.p2().x(), value))

    def setPoints(self : Self, p1 : QPointF, p2 : QPointF) -> None:
        self.setPos(p1)
        self._line.setP2(p2-p1)
        self.setLine(self._line)
        self.onGeometryChange()


class SymbolLineItem(LineItem):
    pass
