from typing import Self
from enum   import StrEnum

from PyQt6.QtCore import QPointF

from ....core.types import HandleId

from .null import NullItem
from .grip import (
    GripItem, MoveGripItem, ResizeGripItem,
    PolylineResizeGripItem, TextResizeGripItem,
    VertexGripItem, SegmentGripItem
)

from .mixin.transform import ItemTransformMixin
from .mixin.change    import ItemChangeMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .mixin.handle import ItemHandlesMixin


class HandleGripKind(StrEnum):
    MOVE     = "move"      # item moving
    RESIZE   = "resize"    # item resizing
    POLYLINE = "polyline"  # polyline resizing
    TEXT     = "text"      # text resizing
    VERTEX   = "vertex"    # vertex e.g. of polyline
    SEGMENT  = "segment"   # segment e.g. of polyline

_HANDLE_GRIP_KIND_MAP = {
    HandleGripKind.MOVE     : MoveGripItem,
    HandleGripKind.RESIZE   : ResizeGripItem,
    HandleGripKind.POLYLINE : PolylineResizeGripItem,
    HandleGripKind.TEXT     : TextResizeGripItem,
    HandleGripKind.VERTEX   : VertexGripItem,
    HandleGripKind.SEGMENT  : SegmentGripItem
}


class HandleItem(ItemChangeMixin, NullItem):
    # instance attributes
    _id   : HandleId
    _grip : GripItem

    def __init__(
        self   : Self,
        id     : HandleId,
        pos    : QPointF | None = None,
        kind   : HandleGripKind = HandleGripKind.MOVE,
        parent : "ItemHandlesMixin" = None
    ) -> None:
        super().__init__(parent)
        self._id = id
        self.setPos(pos or QPointF())
        grip_class = _HANDLE_GRIP_KIND_MAP[kind]
        self._grip = grip_class(self)

    def id(self : Self) -> HandleId:
        return self._id

    def setId(self : Self, id : HandleId) -> None:
        self._id = id

    def onSceneRotationChange(self : Self) -> None:
        for child in self.childItems():
            if hasattr(child, "onSceneRotationChange"):
                child.onSceneRotationChange()

    def isOrigin(self : Self) -> bool:
        parent = self.parentItem()
        if isinstance(parent, ItemTransformMixin):
            return parent.origin() == self.id()
        return False

    def grip(self : Self) -> GripItem:
        return self._grip
