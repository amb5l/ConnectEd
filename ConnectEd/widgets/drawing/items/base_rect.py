__all__ = ["BaseRectangle"]

from typing import Self, Optional, overload

from PyQt6.QtCore    import QPointF, QRectF, QSizeF
from PyQt6.QtWidgets import QWidget, QMenu, QStyleOptionGraphicsItem
from PyQt6.QtGui     import QPainter, QPainterPath

from ....core   import logger

from . import CustomGraphicsRectItem, Element, cmdPlaceElement, \
              KPLoc, KPDef, KPManager

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingView


class BaseRectangle(CustomGraphicsRectItem, Element):
    """Base class for rectangle elements."""
    XML_ATTRS = Element.XML_ATTRS | {
        "size" : (
            "QSizeF", True,
            lambda self, value: self.setSize(value),
            lambda self: self.rect().size()
        )
    }
    MIN_SIZE = QSizeF(1.0, 1.0)
    _MENU_ITEM_NAMES = [
        "Appearance..."
    ]

    _kpm           : KPManager
    _rect          : QRectF
    _bounding_rect : QRectF
    _shape         : QPainterPath

    @overload
    def __init__(
        self : Self,
        rect : QRectF
    ) -> None:
        ...

    @overload
    def __init__(
        self : Self,
        pos  : QPointF,
        size : QSizeF
    ) -> None:
        ...

    @overload
    def __init__(
        self : Self,
        p1   : QPointF,
        p2   : QPointF
    ) -> None:
        ...

    @overload
    def __init__(
        self : Self,
        a1   : float | int,
        a2   : float | int,
        a3   : float | int,
        a4   : float | int
    ) -> None:
        ...

    def __init__(
        self : Self,
        a1   : QRectF | QPointF | float = QRectF(),
        a2   : Optional[QSizeF | QPointF | float] = None,
        a3   : Optional[float | int]              = None,
        a4   : Optional[float | int]              = None
    ) -> None:
        super().__init__()
        self.__init2__(text=None)
        self._kpm = KPManager(self, [KPDef(k, True, False) for k in KPLoc])
        self._shape = QPainterPath()
        if isinstance(a1, QRectF):
            self.setRect(a1)
        elif isinstance(a1, QPointF) and isinstance(a2, QSizeF):
            self.setRect(a1, a2)
        elif isinstance(a1, QPointF) and isinstance(a2, QPointF):
            self.setPoints(a1, a2)
        elif isinstance(a1, (float, int)) and isinstance(a2, (float, int)) \
              and isinstance(a3, (float, int)) and isinstance(a4, (float, int)):
            self.setRect(a1, a2, a3, a4)
        else:
            logger.error(f"Invalid arguments: expected (x, y, w, h), (pos, size), or (rect); got {a1}, {a2}, {a3}, {a4}")

    def setRect(
        self       : Self,
        rect_or_ax : Optional[QRectF | float | int] = None,
        ay         : Optional[float | int]          = None,
        w          : Optional[float | int]          = None,
        h          : Optional[float | int]          = None
    ) -> None:
        # TODO handle minimum size
        if isinstance(rect_or_ax, QRectF):
            super().setRect(rect_or_ax)
        else:
            super().setRect(rect_or_ax, ay, w, h)
        self._rect = self.rect()
        w = self.line.pen.widthF()
        self._bounding_rect = self._rect.adjusted(-w/2, -w/2, w/2, w/2)
        self._shape.clear()
        self._shape.addRect(self._bounding_rect)
        self._kpm.updatePositions()

    def boundingRect(self : Self) -> QRectF:
        return self._bounding_rect

    def shape(self : Self) -> QPainterPath:
        return self._shape

    def paint(
        self    : Self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        painter.setPen(self.line.pen)
        painter.setBrush(self.fill.brush)
        painter.drawRect(self._rect)

    def KPRect(self : Self) -> QRectF:
        return self._rect

    def setKPVisible(self : Self, visible : bool) -> None:
        self._kpm.setVisible(visible)

    def setSize(self : Self, size : QSizeF) -> None:
        self.setRect(0, 0, size.width(), size.height())

    def setPosSize(self : Self, pos : QPointF, size : QSizeF) -> None:
        self.setPos(pos)
        size.setWidth(max(size.width(), self.MIN_SIZE.width()))
        size.setHeight(max(size.height(), self.MIN_SIZE.height()))
        self.setRect(0, 0, size.width(), size.height())

    @overload
    def setPoints(
        self     : Self,
        p1       : QPointF,
        p2       : QPointF
    ) -> None:
        ...

    @overload
    def setPoints(
        self     : Self,
        x1       : float | int,
        y1       : float | int,
        x2       : float | int,
        y2       : float | int
    ) -> None:
        ...

    def setPoints(
        self     : Self,
        p1_or_x1 : QPointF | float | int,
        p2_or_y1 : QPointF | float | int,
        x2       : Optional[float | int] = None,
        y2       : Optional[float | int] = None
    ) -> None:
        if isinstance(p1_or_x1, QPointF) and isinstance(p2_or_y1, QPointF) \
             and x2 is None and y2 is None:
            p1, p2 = p1_or_x1, p2_or_y1
        elif isinstance(p1_or_x1, float | int) \
             and isinstance(p2_or_y1, float | int) \
             and isinstance(x2, float | int) \
             and isinstance(y2, float | int):
            p1, p2 = QPointF(p1_or_x1, p2_or_y1), QPointF(x2, y2)
        else:
            logger.error(f"Invalid arguments: expected (p1, p2) or (x1, y1, x2, y2); got {p1_or_x1}, {p2_or_y1}, {x2}, {y2}")
            return
        rect = QRectF(p1, p2).normalized()
        self.setPosSize(rect.topLeft(), rect.size())

    def setPosSizeOrP2(
        self       : Self,
        pos        : QPointF,
        size_or_p2 : QSizeF | QPointF
    ) -> None:
        if isinstance(size_or_p2, QSizeF):
            self.setPosSize(pos, size_or_p2)
        else:
            self.setPoints(pos, size_or_p2)

    def getPoints(self : Self) -> tuple[QPointF, QPointF]:
        return self.pos(), self.pos() + self.rect().bottomRight()

    def moveKeyPoint(self : Self, kp : KPLoc, delta : QPointF) -> None:
        p1, p2 = self.getPoints()
        d = delta
        match kp:
            case KPLoc.TOP_LEFT:
                self.setPoints(p1 + d, p2)
            case KPLoc.TOP_CENTER:
                self.setPoints(p1.x(), p1.y() + d.y(), p2.x(), p2.y())
            case KPLoc.TOP_RIGHT:
                self.setPoints(p1.x(), p1.y() + d.y(), p2.x() + d.x(), p2.y())
            case KPLoc.CENTER_LEFT:
                self.setPoints(p1.x() + d.x(), p1.y(), p2.x(), p2.y())
            case KPLoc.CENTER:
                self.setPos(self.pos() + d)
            case KPLoc.CENTER_RIGHT:
                self.setPoints(p1.x(), p1.y(), p2.x() + d.x(), p2.y())
            case KPLoc.BOTTOM_LEFT:
                self.setPoints(p1.x() + d.x(), p1.y(), p2.x(), p2.y() + d.y())
            case KPLoc.BOTTOM_CENTER:
                self.setPoints(p1.x(), p1.y(), p2.x(), p2.y() + d.y())
            case KPLoc.BOTTOM_RIGHT:
                self.setPoints(p1, p2 + d)
            case _:
                raise ValueError(f"Invalid key point: {kp}")

    def ctxMenuAppearance(
        self    : Self,
        checked : bool,
        view    : "DrawingView"
    ) -> None:
        view.editAppearance(self)

    @overload
    @classmethod
    def createOrUpdate(
        cls   : Self,
        rect  : QRectF,
        *,
        inst  : Optional[Self] = None
    ) -> "BaseRectangle":
        ...

    @overload
    @classmethod
    def createOrUpdate(
        cls  : Self,
        pos  : QPointF,
        size : QSizeF,
        *,
        inst : Optional[Self] = None
    ) -> "BaseRectangle":
        ...

    @overload
    @classmethod
    def createOrUpdate(
        cls  : Self,
        p1   : QPointF,
        p2   : QPointF,
        *,
        inst : Optional[Self] = None
    ) -> "BaseRectangle":
        ...

    @overload
    @classmethod
    def createOrUpdate(
        cls  : Self,
        ax   : float | int,
        ay   : float | int,
        w    : float | int,
        h    : float | int,
        *,
        inst : Optional[Self] = None
    ) -> "BaseRectangle":
        ...

    @classmethod
    def createOrUpdate(
        cls  : Self,
        a1   : QRectF | QPointF | float | int,
        a2   : Optional[QSizeF | QPointF | float | int] = None,
        a3   : Optional[float | int] = None,
        a4   : Optional[float | int] = None,
        *,
        inst : Optional[Self] = None
    ) -> "BaseRectangle":
        inst = cls() if inst is None else inst
        if isinstance(a1, QRectF) and a2 is None and a3 is None and a4 is None:
            inst.setRect(a1)
        elif isinstance(a1, QPointF) and isinstance(a2, QSizeF) \
             and a3 is None and a4 is None:
            inst.setPosSize(a1, a2)
        elif isinstance(a1, QPointF) and isinstance(a2, QPointF) \
             and a3 is None and a4 is None:
            inst.setPoints(a1, a2)
        elif isinstance(a1, QPointF) and a2 is None \
             and a3 is None and a4 is None:
            inst.setPosSize(a1, cls.MIN_SIZE)
        elif isinstance(a1, float | int) and isinstance(a2, float | int) \
             and isinstance(a3, float | int) and isinstance(a4, float | int):
            inst.setRect(a1, a2, a3, a4)
        else:
            logger.error(f"Invalid arguments: expected (rect), (pos, size), (p1, p2), or (x, y, w, h); got {a1}, {a2}, {a3}, {a4}")
            inst = None
        return inst

class cmdPlaceBaseRectangle(cmdPlaceElement):
    element : BaseRectangle
