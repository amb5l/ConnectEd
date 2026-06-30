from __future__ import annotations

from typing import Self, cast

from PyQt6.QtCore    import QPointF, QRectF
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsRectItem, QGraphicsEllipseItem

from .....core.check import checked
from .....core.types import HandleId, RectHandleId, DataKind

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..handle import HandleItem
    from ..grip   import GripItem, MoveGripItem, ResizeGripItem


class ItemHandlesMixin:
    # instance attributes
    _handles : dict[HandleId, HandleItem]

    @classmethod
    def handleIdType(cls) -> type[HandleId]:
        raise NotImplementedError("Subclass must implement handleIdType")

    @classmethod
    def handleIdKind(cls) -> DataKind:
        raise NotImplementedError("Subclass must implement handleIdKind")

    @classmethod
    def handleGripType(cls, id : HandleId) -> type[GripItem]:
        raise NotImplementedError("Subclass must implement handleGripType")

    def initHandles(self : Self) -> None:
        from ..handle import HandleItem
        self._handles = {}
        for id in self.handleIdType():
            self._handles[id] = HandleItem(
                id=id,
                grip_cls=self.handleGripType(id),
                parent=cast(QGraphicsItem, self)
            )

    def handles(self : Self) -> dict[HandleId, HandleItem]:
        return self._handles

    @checked
    def getHandle(self : Self, id : HandleId | str) -> HandleItem:
        if isinstance(id, str):
            key = self.handleIdType()(id)
        else:
            key = id
        return self._handles[key]

    def setGripsVisible(self : Self, visible : bool) -> None:
        from .select import ItemSelectMixin
        select_mode = self.selectMode() if isinstance(self, ItemSelectMixin) \
            else 0
        for h in self._handles.values():
            h.grip().setVisible(visible and select_mode == 0)


class ItemRectHandlesMixin(ItemHandlesMixin):
    @classmethod
    def handleIdType(cls) -> type[RectHandleId]:
        return RectHandleId

    @classmethod
    def handleIdKind(cls) -> DataKind:
        return DataKind.RECT_HANDLE

    @classmethod
    def handleGripType(cls, id : HandleId) -> type[GripItem]:
        from ..grip import MoveGripItem, ResizeGripItem
        return MoveGripItem if id == RectHandleId.MIDDLE_CENTER \
            else ResizeGripItem

    def handleRect(self : Self) -> QRectF:
        raise NotImplementedError("Subclass must implement this method")

    def updateHandlePositions(self : Self) -> None:
        from .transform import ItemTransformMixin
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
        if isinstance(self, ItemTransformMixin) and hasattr(self, "_ORIGIN"):
            self.updateTransform()

    @checked
    def moveHandleBy(
        self : Self,
        id   : RectHandleId,
        d    : QPointF
    ) -> None:
        from ..base_rect import BaseRectangleMixin
        from .transform import ItemTransformMixin
        if not isinstance(self, QGraphicsRectItem | QGraphicsEllipseItem) \
        or not isinstance(self, ItemTransformMixin) \
        or not isinstance(self, BaseRectangleMixin):
            raise TypeError("Bad host")
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
                self.moveBy(d.x(), d.y())
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
