from typing import Self, Optional

from PyQt6.QtCore    import QPointF, QLineF
from PyQt6.QtWidgets import QGraphicsLineItem, QGraphicsSceneMouseEvent

from ....core.log import logger

from ..properties import PropertySpec

from . import ElementAnchorPointsMixin

from .base_text    import BaseText
from .anchor_point import AnchorPoint


class Tether(QGraphicsLineItem):
    """Tether line between a TetherText anchor and its parent."""

    _item  : "TetherText"
    _line  : QLineF

    def __init__(self, item: "TetherText", visible : bool = False):
        super().__init__(item)  # Parent it to the TetherText
        self._item = item
        self.setVisible(visible)
        self.setFlag( self.GraphicsItemFlag.ItemIgnoresTransformations , False )
        self._line = QLineF()
        self.setLine(self._line)
        self.onSettingsChange()
        self.onPositionChange(self._item.pos())

    def mousePressEvent(self : Self, event : QGraphicsSceneMouseEvent) -> None:
        self._item.mousePressEvent(event)

    def mouseReleaseEvent(self : Self, event : QGraphicsSceneMouseEvent) -> None:
        self._item.mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self : Self, event : QGraphicsSceneMouseEvent) -> None:
        self._item.mouseDoubleClickEvent(event)

    def onSettingsChange(self : Self) -> None:
        self.setPen(self._item.outline.pen)

    def onPositionChange(self : Self, _ : QPointF) -> None:
        cleat : Optional[AnchorPoint] = self._item.parentItem()
        if cleat is None:
            return
        self._line.setP2(cleat.scenePos() - self.scenePos())
        self.setLine(self._line)

class TetherText(BaseText):

    # class attributes
    _PROPERTY_SPECS_TETHER = {
        "Cleat" : PropertySpec(
            type_name   = "str",
            getter      = lambda self: self.cleat(),
            setter      = lambda self, value: self.setCleat(value),
            description = "Parent anchor point"
        )
    }

    # instance attributes
    _tether : Optional[Tether]

    def __init__(self : Self, bare : bool = False) -> None:
        super().__init__(bare=bare)
        self._tether = Tether(self)

    def onSettingsChange(self : Self) -> None:
        self._tether.onSettingsChange()

    def onPositionChange(self : Self, pos : QPointF) -> None:
        self._tether.onPositionChange(pos)

    def onSelectionChange(self : Self, selected : bool) -> None:
        self._tether.setVisible(selected)

    def setOrigin(self : Self, name : str) -> None:
        """Override to update tether line."""
        super().setOrigin(name)
        self._tether.setParentItem(self._origin)
        self._tether.onPositionChange(self.pos())

    def cleat(self : Self) -> str:
        parent = self.parentItem()
        if isinstance(parent, AnchorPoint):
            return parent.name()
        else:
            logger.error(f"Parent is not an AnchorPoint: {type(parent).__name__}")
            return ""

    def setCleat(self : Self, name : str) -> None:
        parent = self.parentItem()
        if isinstance(parent, AnchorPoint):
            grandparent = parent.parentItem()
            if isinstance(grandparent, ElementAnchorPointsMixin):
                self.setParentItem(grandparent.getAnchorPoint(name))
            else:
                logger.error(f"Grandparent is not an ElementAnchorPointsMixin: {type(grandparent).__name__}")
            parent.setName(name)
        else:
            logger.error(f"Parent is not an AnchorPoint: {type(parent).__name__}")

    def getTotalRotation(self) -> float:
        r = 0.0
        item = self
        while item is not None:
            r += item.rotation()
            item = item.parentItem()
        return r % 360
