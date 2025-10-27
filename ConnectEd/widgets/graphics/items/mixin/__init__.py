import uuid

from typing import Self

from PyQt6.QtWidgets import QGraphicsItem

from .....app import settings

from .....core.defs  import Z_DRAWING

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import Appearance


class ItemMixin:
    Z = Z_DRAWING

    _uuid : str
    a     : "Appearance | None"

    def initItem(self : Self | QGraphicsItem, bare : bool = False) -> None:
        from .vertex  import ItemVertexMixin
        from .loc     import ItemLocMixin
        from .origin  import ItemOriginMixin
        from .line    import ItemLineMixin
        from .fill    import ItemFillMixin
        from .quill   import ItemQuillMixin
        from .outline import ItemOutlineMixin
        from .change  import ItemChangeMixin
        from .anchor  import ItemAnchorPointsMixin
        from ...properties import PropertiesMixin
        self.setZValue(self.Z)
        f = QGraphicsItem.GraphicsItemFlag
        self.setFlag( f.ItemIsSelectable              , True )
        self.setFlag( f.ItemSendsGeometryChanges      , True )
        self.setFlag( f.ItemSendsScenePositionChanges , True )
        self.setCacheMode(QGraphicsItem.CacheMode.DeviceCoordinateCache)
        self.resetUuid()
        if isinstance(self, ItemVertexMixin):
            self.initVertices()
        if isinstance(self, ItemLocMixin):
            self.initLoc()
        if isinstance(self, ItemAnchorPointsMixin):
            self.initAnchorPoints()
        if isinstance(self, ItemOriginMixin):
            self.initOrigin()
        if isinstance(self, ItemLineMixin):
            self.initLine()
        if isinstance(self, ItemFillMixin):
            self.initFill()
        if isinstance(self, ItemQuillMixin):
            self.initQuill()
        if isinstance(self, ItemOutlineMixin):
            self.initOutline()
        if isinstance(self, ItemChangeMixin):
            self.onSettingsChange()
            settings().changed.connect(self.onSettingsChange)
        if isinstance(self, PropertiesMixin):
            self.initProperties(bare)

    def __hash__(self : Self | QGraphicsItem):
        return hash(self._uuid)

    def __eq__(self : Self | QGraphicsItem, other : Self | QGraphicsItem):
        if not isinstance(other, ItemMixin):
            return NotImplemented
        return self._uuid == other._uuid

    def resetUuid(self : Self | QGraphicsItem) -> None:
        self._uuid = str(uuid.uuid4())

    def parentSceneRotation(self: Self | QGraphicsItem) -> float:
            """
            Returns the effective rotation angle (degrees) of the parent
            w.r.t. the scene by summing hierarchy.
            """
            angle : float = 0.0
            item  : QGraphicsItem = self.parentItem()
            while item is not None:
                angle += item.rotation()
                item = item.parentItem()
            return angle % 360.0
