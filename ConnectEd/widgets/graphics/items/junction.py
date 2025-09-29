from typing import Self

from PyQt6.QtCore    import QRectF
from PyQt6.QtWidgets import QGraphicsEllipseItem
from PyQt6.QtGui     import QBrush

from ....app import settings

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .wire_vertex import WireVertex


class Junction(QGraphicsEllipseItem):
    # instance attributes
    _rect  : QRectF
    _brush : QBrush

    def __init__(self : Self, parent : "WireVertex") -> None:
        QGraphicsEllipseItem.__init__(self, parent)
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable, True)
        self._rect = QRectF()
        self._brush = QBrush()
        self.onSettingsChange()

    def onSettingsChange(self : Self) -> None:
        size = settings().get("theme/elements/Junction/size")
        self._rect.setLeft(-size/2)
        self._rect.setTop(-size/2)
        self._rect.setRight(size/2)
        self._rect.setBottom(size/2)
        self.setRect(self._rect)
        color = settings().get("theme/elements/Junction/color")
        self._brush.setColor(color)
        self.setBrush(self._brush)
