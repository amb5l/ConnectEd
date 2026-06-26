from __future__ import annotations

from typing import Self, TypeVar, Generic, Protocol, overload

from PyQt6.QtCore    import QPointF, QRectF
from PyQt6.QtWidgets import QGraphicsItem

from .....core.check import checked
from .....core.types import HandleId, RectHandleId, DataKind

from ..handle import HandleItem
from ..grip   import MoveGripItem, ResizeGripItem

from .transform import ItemTransformMixin
from .grip      import ItemGripMixin


T = TypeVar("T", bound=HandleId)

class ItemHandlesMixin(ItemGripMixin, Generic[T]):

    # instance attributes
    _handles : dict[T, HandleItem]

    def handles(self : Self) -> dict[T, HandleItem]:
        return self._handles

    @checked
    def getHandle(self : Self, id : T | str) -> HandleItem:
        if isinstance(id, str):
            id = self.handleIdType()(id)
        return self._handles[id]


class RectItemProtocol(Protocol):
    @overload
    def setPoints(self : Self, p1 : QPointF, p2 : QPointF) -> None: ...

    @overload
    def setPoints(
        self : Self,
        x1 : float | int,
        y1 : float | int,
        x2 : float | int,
        y2 : float | int
    ) -> None: ...


class ItemRectHandlesMixin(ItemHandlesMixin[RectHandleId]):
    # class attributes
    _RESIZE_GRIP_CLS = ResizeGripItem

    @classmethod
    def handleIdType(cls) -> type[RectHandleId]:
        return RectHandleId

    @classmethod
    def handleIdKind(cls) -> DataKind:
        return DataKind.RECT_HANDLE

    # instance attributes
    _handles : dict[RectHandleId, HandleItem]

    @checked
    def initHandles(self : Self) -> None:
        self._handles = {}
        for id in RectHandleId:
            grip_cls = MoveGripItem if id == RectHandleId.MIDDLE_CENTER \
                else self._RESIZE_GRIP_CLS
            handle = HandleItem(id=id, grip_cls=grip_cls, parent=self)
            self._handles[id] = handle

    def handleRect(self : Self) -> QRectF:
        raise NotImplementedError("Subclass must implement this method")

    def updateHandlePositions(self : Self | ItemTransformMixin) -> None:
        if not hasattr(self, "_handles"):
            return
        rect = self.handleRect()
        x0 = rect.topLeft().x()
        y0 = rect.topLeft().y()
        w = rect.width()
        h = rect.height()
        for id in RectHandleId:
            name = id.value
            x = 1.0 if "Right" in name else 0.5 if "Center" in name else 0.0
            y = 1.0 if "Bottom" in name else 0.5 if "Middle" in name else 0.0
            self._handles[id].setPos(QPointF(x0 + (x * w), y0 + (y * h)))
        if hasattr(self, "origin"):
            self.updateTransform()

    @checked
    def moveHandleBy(
        self : Self | QGraphicsItem | RectItemProtocol,
        id   : RectHandleId,
        d    : QPointF
    ) -> None:
        p1 = self.pos() - self.transformOriginPoint()
        p2 = p1 + self.rect().bottomRight()
        match id:
            case RectHandleId.TOP_LEFT:
                self.setPoints(p1 + d, p2)
            case RectHandleId.TOP_CENTER:
                self.setPoints(p1.x(), p1.y() + d.y(), p2.x(), p2.y())
            case RectHandleId.TOP_RIGHT:
                self.setPoints(p1.x(), p1.y() + d.y(), p2.x() + d.x(), p2.y())
            case RectHandleId.MIDDLE_LEFT:
                self.setPoints(p1.x() + d.x(), p1.y(), p2.x(), p2.y())
            case RectHandleId.MIDDLE_CENTER:
                self.moveBy(d)
            case RectHandleId.MIDDLE_RIGHT:
                self.setPoints(p1.x(), p1.y(), p2.x() + d.x(), p2.y())
            case RectHandleId.BOTTOM_LEFT:
                self.setPoints(p1.x() + d.x(), p1.y(), p2.x(), p2.y() + d.y())
            case RectHandleId.BOTTOM_CENTER:
                self.setPoints(p1.x(), p1.y(), p2.x(), p2.y() + d.y())
            case RectHandleId.BOTTOM_RIGHT:
                self.setPoints(p1, p2 + d)
            case _:
                raise ValueError(f"Invalid handle: {id}")
