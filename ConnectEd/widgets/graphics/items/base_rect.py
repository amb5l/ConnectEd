from __future__ import annotations

from typing import Self, overload

from PyQt6.QtCore    import QPointF, QRectF, QSizeF
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsRectItem, \
                            QGraphicsEllipseItem, QMenu
from PyQt6.QtGui     import QAction

from ....core.check import checked
from ....core.defs  import PITCH
from ....core.types import RectHandleId, DataKind

from ..properties import InherentProperty, PropertiesMixin

from .mixin.transform  import ItemTransformMixin
from .mixin.handle     import ItemRectHandlesMixin
from .mixin.primary    import PrimaryItemMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.diagram  import DiagramView


class BaseRectangleMixin(
    ItemTransformMixin,
    ItemRectHandlesMixin,
    PrimaryItemMixin
):
    """Base mixin class for rectangle-like items."""

    # class attributes
    _ORIGIN = RectHandleId.MIDDLE_CENTER
    _PROPERTIES = \
        ItemTransformMixin._PROPERTIES_RECT_ORIGIN | \
        ItemTransformMixin._PROPERTIES_POS | \
        ItemTransformMixin._PROPERTIES_ROTATE | \
        ItemTransformMixin._PROPERTIES_MIRROR | \
        {
            "Width" : InherentProperty["BaseRectangleMixin"](
                kind   = DataKind.FLOAT,
                getter = lambda self: self.width(),
                setter = lambda self, value: self.setWidth(value)
            ),
            "Height" : InherentProperty["BaseRectangleMixin"](
                kind   = DataKind.FLOAT,
                getter = lambda self: self.height(),
                setter = lambda self, value: self.setHeight(value)
            )
        } | \
        PrimaryItemMixin._PROPERTIES_LINE | \
        PrimaryItemMixin._PROPERTIES_FILL
    _MIN_SIZE = QSizeF(1.0, 1.0)

    @overload
    def __init__(
        self  : Self,
        p1    : QPointF | None = None,
        p2    : QPointF | None = None,
        fresh : bool = True
    ) -> None:
        ...

    @overload
    def __init__(
        self  : Self,
        pos   : QPointF | None = None,
        size  : QSizeF | None = None,
        fresh : bool = True
    ) -> None:
        ...

    @checked
    def __init__(  # pyright: ignore[reportInconsistentOverload]
        self       : Self,
        p1_or_pos  : QPointF | None = None,
        p2_or_size : QPointF | QSizeF | None = None,
        fresh      : bool = True
    ) -> None:
        super().__init__()
        self.initItem(fresh)
        p1_or_pos = p1_or_pos or QPointF()
        p2_or_size = p2_or_size or QSizeF(0, 0)
        if isinstance(p2_or_size, QSizeF):
            p2_or_size = QPointF(
                p1_or_pos.x() + p2_or_size.width(),
                p1_or_pos.y() + p2_or_size.height()
            )
        self.setPoints(p1_or_pos, p2_or_size)
        self.onGeometryChanged()

    def onGeometryChanged(self : Self) -> None:
        self.updateHandlePositions()

    @overload
    def setRect(
        self : Self,
        rect : QRectF
    ) -> None:
        ...

    @overload
    def setRect(
        self : Self,
        ax : float | int,
        ay : float | int,
        w  : float | int,
        h  : float | int
    ) -> None:
        ...

    def setRect(  # pyright: ignore[reportInconsistentOverload]
        self : Self,
        rect_or_ax : QRectF | float | int,
        ay         : float | int | None = None,
        w          : float | int | None = None,
        h          : float | int | None = None
    ) -> None:
        if not isinstance(self, QGraphicsRectItem | QGraphicsEllipseItem):
            raise TypeError("Bad host")
        old = self.rect()
        if isinstance(rect_or_ax, QRectF) \
        and ay is None and w is None and h is None:
            rect = rect_or_ax
        elif isinstance(rect_or_ax, float | int) \
        and isinstance(ay, float | int) \
        and isinstance(w, float | int) \
        and isinstance(h, float | int):
            rect = QRectF(rect_or_ax, ay, w, h)
        else:
            raise TypeError("bad arguments")
        if isinstance(self, QGraphicsRectItem):
            QGraphicsRectItem.setRect(self, rect)
        else:
            QGraphicsEllipseItem.setRect(self, rect)
        new = self.rect()
        self.onGeometryChanged()
        if isinstance(self, PropertiesMixin):
            names : list[str] = []
            if old.width() != new.width():
                names.append("Width")
            if old.height() != new.height():
                names.append("Height")
            if names:
                self.properties.signalChanges(names)

    def width(self : Self) -> float:
        if not isinstance(self, QGraphicsRectItem | QGraphicsEllipseItem):
            raise TypeError("Bad host")
        return self.rect().width()

    @checked
    def setWidth(self : Self, width : float | int) -> None:
        if not isinstance(self, QGraphicsRectItem | QGraphicsEllipseItem):
            raise TypeError("Bad host")
        rect = self.rect()
        rect.setWidth(width)
        self.setRect(rect)

    def height(self : Self) -> float:
        if not isinstance(self, QGraphicsRectItem | QGraphicsEllipseItem):
            raise TypeError("Bad host")
        return self.rect().height()

    @checked
    def setHeight(self : Self, height : float | int) -> None:
        if not isinstance(self, QGraphicsRectItem | QGraphicsEllipseItem):
            raise TypeError("Bad host")
        rect = self.rect()
        rect.setHeight(height)
        self.setRect(rect)

    @overload
    def setPoints(
        self : Self,
        p1   : QPointF,
        p2   : QPointF
    ) -> None:
        ...

    @overload
    def setPoints(
        self : Self,
        x1   : float | int,
        y1   : float | int,
        x2   : float | int,
        y2   : float | int
    ) -> None:
        ...

    @checked
    def setPoints(  # pyright: ignore[reportInconsistentOverload]
        self : Self,
        p1_x1 : QPointF | float | int,
        p2_y1 : QPointF | float | int,
        x2    : float | int | None = None,
        y2    : float | int | None = None
    ) -> None:
        if not isinstance(self, QGraphicsRectItem | QGraphicsEllipseItem):
            raise TypeError("Bad host")
        if isinstance(p1_x1, QPointF) \
        and isinstance(p2_y1, QPointF) \
        and x2 is None and y2 is None:
            x1 = p1_x1.x()
            y1 = p1_x1.y()
            x2 = p2_y1.x()
            y2 = p2_y1.y()
        elif isinstance(p1_x1, float | int) \
        and isinstance(p2_y1, float | int) \
        and isinstance(x2, float | int) \
        and isinstance(y2, float | int):
            x1 = p1_x1
            y1 = p2_y1
            x2 = x2
            y2 = y2
        else:
            raise TypeError("bad arguments")
        w = max(abs(x2-x1), PITCH)
        h = max(abs(y2-y1), PITCH)
        rect = self.rect()
        rect.setSize(QSizeF(w, h))
        self.setRect(rect)
        origin_offset = self.transformOriginPoint()
        target_pos = QPointF(min(x1, x2), min(y1, y2)) + origin_offset
        self.setPos(target_pos)

    def handleRect(self : Self) -> QRectF:
        if not isinstance(self, QGraphicsRectItem | QGraphicsEllipseItem):
            raise TypeError("Bad host")
        return self.rect()

    @checked
    def ctxMenuItems(
        self : Self,
        view : DiagramView,
        spos : QPointF
    ) -> list[QAction | QMenu]:
        if not isinstance(self, QGraphicsItem): raise TypeError("Bad host")
        return [
            view.action("Appearance...", lambda: view.editAppearance(self)),
            view.action("Properties...", lambda: view.editItemProperties(self))
        ]


class BaseRectangleItem(BaseRectangleMixin, QGraphicsRectItem):
    """Base class for rectangle items."""
    pass
