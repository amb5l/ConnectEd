from typing import Self

from PyQt6.QtCore    import QPointF, QLineF, QXmlStreamWriter
from PyQt6.QtWidgets import QGraphicsLineItem, QGraphicsSceneMouseEvent

from ....app import logger

from ..properties import PropertySpec

from .mixin.anchor import ElementAnchorPointsMixin

from .base_text    import BaseText
from .anchor_point import APName, AnchorPoint


class Tether(QGraphicsLineItem):
    """Tether line between a TetherText anchor and its parent."""

    _item  : "TetherText"
    _line  : QLineF

    def __init__(self : Self, item : "TetherText", visible : bool = False):
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
        cleat : AnchorPoint | None = self._item.parentItem()
        if cleat is None:
            return
        self._line.setP2(cleat.scenePos() - self.scenePos())
        self.setLine(self._line)

    def toXml(self : Self, xw : QXmlStreamWriter) -> str:
        pass  # no need to serialise


class TetherText(BaseText):
    # class attributes
    _PROPERTY_SPECS_CLEAT = {
        "Cleat" : PropertySpec(
            type_name   = "APName",
            getter      = lambda self: self.cleat(),
            setter      = lambda self, value: self.setCleat(value),
            description = "Parent anchor point"
        )
    }

    # instance attributes
    _tether : Tether | None
    _cleat  : APName | None

    def __init__(self : Self, bare : bool = False) -> None:
        self._tether = None
        self._cleat  = None
        super().__init__(bare=bare)
        self._tether = Tether(self)

    def onSettingsChange(self : Self) -> None:
        if self._tether is not None:
            self._tether.onSettingsChange()

    def onPositionChange(self : Self, pos : QPointF) -> None:
        self._tether.onPositionChange(pos)

    def onSelectionChange(self : Self, selected : bool) -> None:
        self._tether.setVisible(selected)

    def setOriginAPName(self : Self, name : APName) -> None:
        """Override to update tether line."""
        super().setOriginAPName(name)
        # parent to origin anchor point
        self._tether.setParentItem(self._origin.parentItem())
        self._tether.onPositionChange(self.pos())

    def cleat(self : Self) -> APName:
        parent = self.parentItem()
        if parent is None:
            return self._cleat  # workaround for deserialization
        elif isinstance(parent, AnchorPoint):
            return parent.name()
        else:
            logger().error(f"Parent is not an AnchorPoint: {type(parent).__name__}")
            return APName.Undefined

    def setCleat(self : Self, name : APName) -> None:
        self._cleat = name
        parent = self.parentItem()
        if parent is None:  # handle deserialization
            return
        if isinstance(parent, AnchorPoint):
            grandparent = parent.parentItem()
            if isinstance(grandparent, ElementAnchorPointsMixin):
                self.setParentItem(grandparent.getAnchorPoint(name))
            else:
                logger().error(f"Grandparent is not an ElementAnchorPointsMixin: {type(grandparent).__name__}")
            parent.setName(name)
        else:
            logger().error(f"Parent is not an AnchorPoint: {type(parent).__name__}")
