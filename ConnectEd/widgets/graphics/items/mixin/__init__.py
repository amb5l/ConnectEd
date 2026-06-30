import uuid

from typing import Self

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QGraphicsItem

from .....core.check import checked
from .....core.defs  import Z_DRAWING

from .names        import ItemNamesMixin
from .move         import ItemMoveMixin


class ItemMixin(ItemNamesMixin, ItemMoveMixin):
    Z = Z_DRAWING

    _uuid : str

    @checked
    def initItem(self : Self, fresh : bool = True) -> None:
        from ...properties  import PropertiesMixin
        from .settings      import ItemSettingsMixin
        from .presentation  import ItemPresentationMixin
        from .select        import ItemSelectMixin
        from .handle        import ItemHandlesMixin
        from .edge_loc      import ItemEdgeLocMixin
        from .transform     import ItemTransformMixin
        from .change        import ItemChangeMixin
        from .subscribe     import ItemSubscribeMixin
        from .shape         import ItemShapeMixin
        if not isinstance(self, QGraphicsItem):
            raise TypeError("Bad host")
        self.setZValue(self.Z)
        f = QGraphicsItem.GraphicsItemFlag
        self.setFlag( f.ItemIsSelectable              , True )
        self.setFlag( f.ItemSendsGeometryChanges      , True )
        self.setFlag( f.ItemSendsScenePositionChanges , True )
        self.setCacheMode(QGraphicsItem.CacheMode.DeviceCoordinateCache)
        self._resetUuid()
        if isinstance(self, ItemSettingsMixin):
            self.initSettings()
        if isinstance(self, ItemPresentationMixin):
            self.initPresentation()
        if isinstance(self, ItemSelectMixin):
            self.initSelect()
        if isinstance(self, ItemHandlesMixin):
            self.initHandles()
        if isinstance(self, PropertiesMixin):
            self.initProperties(fresh)
        if isinstance(self, ItemEdgeLocMixin):
            self.initEdgeLoc()
        if isinstance(self, ItemTransformMixin):
            self.initTransform()
        if isinstance(self, ItemChangeMixin):
            self.initChange()
        if isinstance(self, ItemSubscribeMixin):
            self.initSubscribe()
        if isinstance(self, ItemShapeMixin):
            self.initShape()
        if isinstance(self, PropertiesMixin):
            self.setLive(fresh)

    def __hash__(self : Self):
        return hash(self._uuid)

    def __eq__(self : Self, other : object) -> bool:
        return isinstance(other, ItemMixin) and self._uuid == other._uuid

    def savePos(self : Self) -> QPointF:
        if not isinstance(self, QGraphicsItem):
            raise TypeError("Bad host")
        return self.scenePos()

    @checked
    def restorePos(self : Self, pos : QPointF) -> None:
        self.moveRestore(pos)

    def topParentItem(self : Self) -> QGraphicsItem | None:
        if not isinstance(self, QGraphicsItem):
            raise TypeError("Bad host")
        item = self.parentItem()
        while isinstance(item, QGraphicsItem) and item.parentItem() is not None:
            item = item.parentItem()
        return item

    def _resetUuid(self : Self) -> None:
        self._uuid = str(uuid.uuid4())
