import uuid

from typing import Self

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QGraphicsItem

from .....core.check import checked
from .....core.defs  import Z_DRAWING

from ...properties import PropertiesMixin

from .presentation import ItemPresentationMixin
from .select       import ItemSelectMixin
from .change       import ItemChangeMixin
from .clone        import ItemCloneMixin
from .xml          import ItemXmlMixin
from .menu         import ItemMenuMixin


class ItemNamesMixin:
    def settingsName(self : Self | QGraphicsItem) -> str:
        return self.__class__.__name__.removesuffix("Item")

    def resourcesName(self : Self | QGraphicsItem) -> str:
        return self.__class__.__name__.removesuffix("Item")


class ItemMoveMixin:
    """Methods to support moving items."""

    def moveSave(self : Self | QGraphicsItem) -> QPointF:
        return self.scenePos()

    @checked
    def moveRestore(self : Self | QGraphicsItem, pos : QPointF) -> None:
        self.moveBy(pos - self.scenePos())


class ItemMixin(ItemNamesMixin, ItemMoveMixin):
    Z = Z_DRAWING

    _uuid : str

    @checked
    def initItem(self : Self | QGraphicsItem, fresh : bool = True) -> None:
        from ...properties  import PropertiesMixin
        from .settings      import ItemSettingsMixin
        from .presentation  import ItemPresentationMixin
        from .select        import ItemSelectMixin
        from .handle        import ItemHandlesMixin
        from .loc           import ItemLocMixin
        from .transform     import ItemTransformMixin
        from .change        import ItemChangeMixin
        from .shape         import ItemShapeMixin
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
            self.initProperties(fresh, defer_texts=fresh)
        if isinstance(self, ItemTransformMixin):
            self.initTransform()
        if isinstance(self, ItemLocMixin):
            self.initLoc()
        if isinstance(self, PropertiesMixin) and fresh:
            self.attachPropertyTexts()
        if isinstance(self, ItemChangeMixin):
            self.initChange()
        if isinstance(self, ItemShapeMixin):
            self.initShape()
        if isinstance(self, PropertiesMixin):
            self.properties.setNotify(fresh)

    def __hash__(self : Self | QGraphicsItem):
        return hash(self._uuid)

    def __eq__(self : Self | QGraphicsItem, other : Self | QGraphicsItem):
        if not isinstance(other, ItemMixin):
            return NotImplemented
        return self._uuid == other._uuid

    def savePos(self : Self | QGraphicsItem) -> QPointF:
        return self.scenePos()

    @checked
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


class PrimaryItemMixin(
    ItemMixin,
    ItemPresentationMixin,
    ItemSelectMixin,
    ItemChangeMixin,
    ItemCloneMixin,
    ItemXmlMixin,
    ItemMenuMixin,
    PropertiesMixin
):
    pass
