from typing import Self

from PyQt6.QtCore    import Qt, QPointF, QLineF
from PyQt6.QtWidgets import QGraphicsLineItem
from PyQt6.QtGui     import QPainterPath, QPainterPathStroker

from ....app import settings

from ..properties import PropertySpec

from .anchor_point import AnchorPoint

from .mixin        import ElementMixin
from .mixin.shape  import ElementShapeMixin
from .mixin.anchor import ElementAnchorPointsMixin
from .mixin.line   import ElementLineMixin
from .mixin.change import ElementChangeMixin
from .mixin.clone  import ElementCloneMixin
from .mixin.xml    import ElementXmlMixin
from .mixin.menu   import ElementMenuMixin


class Line(
    ElementMixin,
    ElementShapeMixin,
    ElementAnchorPointsMixin,
    ElementLineMixin,
    ElementChangeMixin,
    ElementCloneMixin,
    ElementXmlMixin,
    ElementMenuMixin,
    QGraphicsLineItem
):
    # class attributes
    _PROPERTY_SPECS = \
        {
            "X1" : PropertySpec(
                type_name = "float",
                getter    = lambda self: self.x1(),
                setter    = lambda self, value: self.setX1(value)
            ),
            "Y1" : PropertySpec(
                type_name = "float",
                getter    = lambda self: self.y1(),
                setter    = lambda self, value: self.setY1(value)
            ),
            "X2" : PropertySpec(
                type_name = "float",
                getter    = lambda self: self.x2(),
                setter    = lambda self, value: self.setX2(value)
            ),
            "Y2" : PropertySpec(
                type_name = "float",
                getter    = lambda self: self.y2(),
                setter    = lambda self, value: self.setY2(value)
            )
        } | \
        ElementLineMixin._PROPERTY_SPECS_LINE

    # instance attributes
    _line : QLineF

    def __init__(
        self : Self,
        p1   : QPointF | None = None,
        p2   : QPointF | None = None
    ) -> None:
        QGraphicsLineItem.__init__(self)
        self.initElement()
        if p1 is None:
            p1 = QPointF()
        if p2 is None:
            p2 = QPointF()
        self._line = QLineF()
        self.setP1P2(p1, p2)

    def onGeometryChange(self : Self) -> None:
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
        stroker.setCapStyle(Qt.PenCapStyle.SquareCap)
        stroker.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        stroker_path = stroker.createStroke(line_path)
        self._hshape = stroker_path

    def initAnchorPoints(self : Self) -> None:
        self._anchor_points = {
            "P1" : AnchorPoint(
                name   = "P1",
                pos    = QPointF(0, 0),
                resize = True,
                parent = self
            ),
            "P2" : AnchorPoint(
                name   = "P2",
                pos    = QPointF(0, 0),
                resize = True,
                parent = self
            )
        }

    def getMenuItems(self : Self) -> list[str]:
        return ["Appearance..."]

    def p1(self : Self) -> QPointF:
        return self.pos()

    def setP1(self : Self, pos : QPointF) -> None:
        self.setP1P2(pos, self.p2())

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
        self.setP1P2(self.p1(), pos)

    def x2(self : Self) -> float:
        return self._line.p2().x()

    def setX2(self : Self, value : float) -> None:
        self.setP2(QPointF(value, self.p2().y()))

    def y2(self : Self) -> float:
        return self.p2().y()

    def setY2(self : Self, value : float) -> None:
        self.setP2(QPointF(self.p2().x(), value))

    def setP1P2(self : Self, p1 : QPointF, p2 : QPointF) -> None:
        print(
            f"setP1P2: ({p1.x()}, {p1.y()}) -> ({p2.x()}, {p2.y()})",
            "brect", self.boundingRect()
        )
        self.setPos(p1)
        self._line.setP2(p2-p1)
        self.setLine(self._line)
        self.onGeometryChange()

    def moveAnchorPointBy(self : Self, name : str, delta : QPointF) -> None:
            match name:
                case "P1":
                    self.setP1(self.p1() + delta)
                case "P2":
                    self.setP2(self.p2() + delta)
                case _:
                    raise ValueError(f"Invalid anchor point: {name}")

    def shape(self : Self) -> QPainterPath:
        return self._hshape
