import uuid

from typing import Self

from PyQt6.QtWidgets import QGraphicsItem

from .....app import settings

from .....core.defs  import Z_DRAWING


class ElementMixin:
    Z = Z_DRAWING

    uuid : str

    def initElement(self : Self, bare : bool = False) -> None:
        f = QGraphicsItem.GraphicsItemFlag
        self.setFlag( f.ItemIsSelectable              , True )
        self.setFlag( f.ItemSendsGeometryChanges      , True )
        self.setFlag( f.ItemSendsScenePositionChanges , True )
        self.setCacheMode(QGraphicsItem.CacheMode.DeviceCoordinateCache)
        self.resetUuid()
        if hasattr(self, "initBoundShape"):
            self.initBoundShape()
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
            settings().changed.connect(self.onSettingsChange)

    def __hash__(self):
        return hash(self.uuid)

    def __eq__(self, other):
        if not isinstance(other, ElementMixin):
            return NotImplemented
        return self.uuid == other.uuid

    def resetUuid(self : Self) -> None:
        self.uuid = str(uuid.uuid4())
