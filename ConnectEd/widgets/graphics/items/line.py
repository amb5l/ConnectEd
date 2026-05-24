from typing import Self

from PyQt6.QtCore    import QPointF, QLineF
from PyQt6.QtWidgets import QGraphicsLineItem, QMenu
from PyQt6.QtGui     import QAction

from ....core.check import checked
from ....core.types import DataKind, LineHandleId

from ..properties import InherentProperty

from .handle import HandleItem
from .grip   import ResizeGripItem

from .mixin           import PrimaryItemMixin
from .mixin.transform import ItemTransformMixin
from .mixin.handle    import ItemHandlesMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.drawing import DrawingView


class LineItem(
    ItemTransformMixin,
    ItemHandlesMixin[LineHandleId],
    PrimaryItemMixin,
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
        PrimaryItemMixin._PROPERTIES_LINE

    @classmethod
    def handleIdType(cls) -> type[LineHandleId]:
        return LineHandleId

    @classmethod
    def handleIdKind(cls) -> DataKind:
        return DataKind.LINE_HANDLE

    # instance attributes
    _line : QLineF

    _line_color = None  # enable per-item appearance control
    _line_width = None  # enable per-item appearance control
    _line_style = None  # enable per-item appearance control

    @checked
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

    @checked
    def initHandles(self : Self) -> None:
        self._handles = {
            LineHandleId.P1 : HandleItem(
                id       = LineHandleId.P1,
                pos      = QPointF(0, 0),
                grip_cls = ResizeGripItem,
                parent   = self
            ),
            LineHandleId.P2 : HandleItem(
                id       = LineHandleId.P2,
                pos      = QPointF(0, 0),
                grip_cls = ResizeGripItem,
                parent   = self
            )
        }

    @checked
    def moveHandleBy(
        self : Self,
        id   : LineHandleId,
        d    : QPointF
    ) -> None:
        match id:
            case LineHandleId.P1:
                self.setP1(self.p1() + d)
            case LineHandleId.P2:
                self.setP2(self.p2() + d)

    def updateHandles(self : Self) -> None:
        self._handles[LineHandleId.P2].setPos(self._line.p2())

    def p1(self : Self) -> QPointF:
        return self.pos()

    @checked
    def setP1(self : Self, pos : QPointF) -> None:
        self.setPoints(pos, self.p2())

    def x1(self : Self) -> float:
        return self.p1().x()

    @checked
    def setX1(self : Self, value : float) -> None:
        self.setP1(QPointF(value, self.p1().y()))
        self.properties.signalChanges("X1")

    def y1(self : Self) -> float:
        return self.p1().y()

    @checked
    def setY1(self : Self, value : float) -> None:
        self.setP1(QPointF(self.p1().x(), value))
        self.properties.signalChanges("Y1")

    def p2(self : Self) -> QPointF:
        return self.pos() + self.line().p2()

    @checked
    def setP2(self : Self, pos : QPointF) -> None:
        self.setPoints(self.p1(), pos)

    def x2(self : Self) -> float:
        return self.p2().x()

    @checked
    def setX2(self : Self, value : float) -> None:
        self.setP2(QPointF(value, self.p2().y()))
        self.properties.signalChanges("X2")

    def y2(self : Self) -> float:
        return self.p2().y()

    @checked
    def setY2(self : Self, value : float) -> None:
        self.setP2(QPointF(self.p2().x(), value))
        self.properties.signalChanges("Y2")

    @checked
    def setPoints(self : Self, p1 : QPointF, p2 : QPointF) -> None:
        self.setPos(p1)
        self._line.setP2(p2-p1)
        self.setLine(self._line)
        self.updateHandles()

    @checked
    def ctxMenuItems(self : Self, view : "DrawingView", _spos : QPointF) -> list[QAction | QMenu]:
        return [
            view.action("Appearance...", lambda: view.ui.editAppearance(self)),
            view.action("Properties...", lambda: view.ui.editItemProperties(self))
        ]
