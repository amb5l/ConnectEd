import uuid

from typing import Self

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QGraphicsItem

from .....core.defs  import Z_DRAWING

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import Appearance


class ItemSettingsMixin:
    def settingsName(self : Self | QGraphicsItem) -> str:
        return self.__class__.__name__.replace("Item", "")


class ItemMoveMixin:
    """Methods to support moving items."""

    def moveSave(self : Self | QGraphicsItem) -> QPointF:
        return self.scenePos()

    def moveRestore(self : Self | QGraphicsItem, pos : QPointF) -> None:
        self.moveBy(pos - self.scenePos())


class ItemMixin(ItemSettingsMixin, ItemMoveMixin):
    Z = Z_DRAWING

    _uuid : str
    a     : "Appearance | None"

    def initItem(self : Self | QGraphicsItem, fresh : bool = True) -> None:
        from ...properties import PropertiesMixin
        from .origin  import ItemOriginMixin
        from .handle  import ItemHandlesMixin
        from .loc     import ItemLocMixin
        from .pos     import ItemPosMixin
        from .rotate  import ItemRotateMixin
        from .change  import ItemChangeMixin
        from .line    import ItemLineMixin
        from .fill    import ItemFillMixin
        from .quill   import ItemQuillMixin
        from .outline import ItemOutlineMixin
        from .bound   import ItemBoundMixin
        from .shape   import ItemShapeMixin
        self.setZValue(self.Z)
        f = QGraphicsItem.GraphicsItemFlag
        self.setFlag( f.ItemIsSelectable              , True )
        self.setFlag( f.ItemSendsGeometryChanges      , True )
        self.setFlag( f.ItemSendsScenePositionChanges , True )
        self.setCacheMode(QGraphicsItem.CacheMode.DeviceCoordinateCache)
        self._resetUuid()
        if isinstance(self, ItemOriginMixin):
            self.initOrigin()
        if isinstance(self, ItemHandlesMixin):
            self.initHandles()
        if isinstance(self, ItemLocMixin):
            self.initLoc()
        if isinstance(self, ItemPosMixin):
            self.initPos()
        if isinstance(self, ItemRotateMixin):
            self.initRotate()
        if isinstance(self, ItemChangeMixin):
            self.initChange()
        if isinstance(self, ItemLineMixin):
            self.initLine()
        if isinstance(self, ItemFillMixin):
            self.initFill()
        if isinstance(self, ItemQuillMixin):
            self.initQuill()
        if isinstance(self, ItemOutlineMixin):
            self.initOutline()
        if isinstance(self, ItemBoundMixin):
            self.initBound()
        if isinstance(self, ItemShapeMixin):
            self.initShape()
        if isinstance(self, PropertiesMixin):
            self.initProperties(fresh)

    def __hash__(self : Self | QGraphicsItem):
        return hash(self._uuid)

    def __eq__(self : Self | QGraphicsItem, other : Self | QGraphicsItem):
        if not isinstance(other, ItemMixin):
            return NotImplemented
        return self._uuid == other._uuid

    def savePos(self : Self | QGraphicsItem) -> QPointF:
        return self.scenePos()

    def restorePos(self : Self | QGraphicsItem, pos : QPointF) -> None:
        self.setPos(pos - self.scenePos())

    def topParentItem(self : Self | QGraphicsItem) -> QGraphicsItem | None:
        item = self.parentItem()
        if item is None:
            return None
        while item.parentItem() is not None:
            item = item.parentItem()
        return item

    def _resetUuid(self : Self | QGraphicsItem) -> None:
        self._uuid = str(uuid.uuid4())
