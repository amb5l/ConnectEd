import uuid

from typing import Self

from PyQt6.QtWidgets import QGraphicsItem

from .....core.defs  import Z_DRAWING

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import Appearance


class ItemSettingsMixin:
    def settingsName(self : Self | QGraphicsItem) -> str:
        return self.__class__.__name__


class ItemMixin(ItemSettingsMixin):
    Z = Z_DRAWING

    _uuid : str
    a     : "Appearance | None"

    def initItem(self : Self | QGraphicsItem, bare : bool = False) -> None:
        from ...properties import PropertiesMixin
        from .handle  import ItemHandlesMixin
        from .loc     import ItemLocMixin
        from .pos_rot import ItemPosRotMixin
        from .change  import ItemChangeMixin
        from .line    import ItemLineMixin
        from .fill    import ItemFillMixin
        from .quill   import ItemQuillMixin
        from .outline import ItemOutlineMixin
        self.setZValue(self.Z)
        f = QGraphicsItem.GraphicsItemFlag
        self.setFlag( f.ItemIsSelectable              , True )
        self.setFlag( f.ItemSendsGeometryChanges      , True )
        self.setFlag( f.ItemSendsScenePositionChanges , True )
        self.setCacheMode(QGraphicsItem.CacheMode.DeviceCoordinateCache)
        self._resetUuid()
        if isinstance(self, ItemHandlesMixin):
            self.initHandles()
        if isinstance(self, ItemLocMixin):
            self.initLoc()
        if isinstance(self, ItemPosRotMixin):
            self.initPosRot()
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
        if isinstance(self, PropertiesMixin):
            self.initProperties(bare)

    def __hash__(self : Self | QGraphicsItem):
        return hash(self._uuid)

    def __eq__(self : Self | QGraphicsItem, other : Self | QGraphicsItem):
        if not isinstance(other, ItemMixin):
            return NotImplemented
        return self._uuid == other._uuid

    def topParentItem(self : Self | QGraphicsItem) -> QGraphicsItem | None:
        item = self.parentItem()
        if item is None:
            return None
        while item.parentItem() is not None:
            item = item.parentItem()
        return item

    def _resetUuid(self : Self | QGraphicsItem) -> None:
        self._uuid = str(uuid.uuid4())
