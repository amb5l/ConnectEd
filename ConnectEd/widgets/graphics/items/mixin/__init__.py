import uuid

from typing import Self

from PyQt6.QtWidgets import QGraphicsItem

from .....app import settings

from .....core.defs  import Z_DRAWING

from .....core.utils import hasAnyAttr

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import Appearance


class ElementMixin:
    Z = Z_DRAWING

    _uuid : str
    a     : "Appearance | None"

    def initElement(self : Self, bare : bool = False) -> None:
        from .. import Appearance
        self.setZValue(self.Z)
        f = QGraphicsItem.GraphicsItemFlag
        self.setFlag( f.ItemIsSelectable              , True )
        self.setFlag( f.ItemSendsGeometryChanges      , True )
        self.setFlag( f.ItemSendsScenePositionChanges , True )
        self.setCacheMode(QGraphicsItem.CacheMode.DeviceCoordinateCache)
        self.resetUuid()
        if hasattr(self, "initBoundShape"):
            self.initBoundShape()
        if hasattr(self, "initLoc"):
            self.initLoc()
        if hasattr(self, "initLine"):
            self.initLine()
        if hasattr(self, "initFill"):
            self.initFill()
        if hasattr(self, "initQuill"):
            self.initQuill()
        if hasattr(self, "initOutline"):
            self.initOutline()
        if hasattr(self, "initAnchorPoints"):
            self.initAnchorPoints()
        if hasattr(self, "initOrigin"):
            self.initOrigin()
        if hasattr(self, "initProperties"):
            self.initProperties(bare)
        if hasattr(self, "onSettingsChange"):
            self.onSettingsChange()
            settings().changed.connect(self.onSettingsChange)

    def __hash__(self : Self):
        return hash(self._uuid)

    def __eq__(self : Self, other):
        if not isinstance(other, ElementMixin):
            return NotImplemented
        return self._uuid == other._uuid

    def resetUuid(self : Self) -> None:
        self._uuid = str(uuid.uuid4())

    def parentSceneRotation(self: Self) -> float:
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
