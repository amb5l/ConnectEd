from typing import Self

from PyQt6.QtCore    import QRectF
from PyQt6.QtWidgets import QGraphicsEllipseItem
from PyQt6.QtGui     import QBrush

from ConnectEd.widgets.graphics.items.mixin.change import ElementChangeMixin

from ....app import settings

from .mixin.line import ElementLineMixin
from .mixin.fill import ElementFillMixin

from .mixin.change import ElementChangeMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .conn_vtx import ConnVtx


class Junction(
    ElementLineMixin,
    ElementFillMixin,
    ElementChangeMixin,
    QGraphicsEllipseItem
):
    # instance attributes
    _rect  : QRectF
    _brush : QBrush

    def __init__(self : Self, parent : "ConnVtx") -> None:
        QGraphicsEllipseItem.__init__(self, parent)
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable, True)
        self._rect = QRectF()
        self._brush = QBrush()
        self.initLine()
        self.initFill()
        self.onSettingsChange()

    def onGeometryChange(self : Self) -> None:
        size = settings().get("theme/elements/Junction/size")
        self._rect.setLeft(-size/2)
        self._rect.setTop(-size/2)
        self._rect.setRight(size/2)
        self._rect.setBottom(size/2)
        self.setRect(self._rect)
