from typing import Self

from PyQt6.QtCore    import QPointF, QLineF, QXmlStreamWriter
from PyQt6.QtWidgets import QGraphicsLineItem, QGraphicsSceneMouseEvent

from ....app import logger

from ..properties import PropertySpec

from .mixin.anchor import ItemAnchorPointsMixin

from .base_text    import BaseText
from .anchor_point import AnchorPoint


class Tether(QGraphicsLineItem):
    """Tether line between a TetherText origin and its parent cleat."""

    _item  : "TetherText"

    def __init__(self : Self, item : "TetherText", visible : bool = False):
        super().__init__(item)  # Parent it to the TetherText
        self._item = item
        self.setVisible(visible)
        self.setFlag( self.GraphicsItemFlag.ItemIgnoresTransformations , False )
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
        if (cleat := self.cleat()) is None:
            return
        line = self.line()
        line.setP2(self.mapFromItem(cleat, QPointF(0, 0)))
        self.setLine(line)

    def cleat(self : Self) -> AnchorPoint | None:
        return self._item.parentItem()

    def toXml(self : Self, xw : QXmlStreamWriter) -> str:
        pass  # no need to serialise


class TetherText(BaseText):
    # class attributes
    _PROPERTY_SPECS_CLEAT = {
        "Cleat" : PropertySpec(
            type_name   = "str",
            getter      = lambda self: self.getCleatAPName(),
            setter      = lambda self, value: self.setCleatAPName(value),
            description = "Parent anchor point"
        )
    }

    # instance attributes
    _tether      : Tether | None
    _cleat       : str | None
    _cleat_shown : bool

    def __init__(self : Self, bare : bool = False) -> None:
        self._tether      = None
        self._cleat       = None
        self._cleat_shown = False
        super().__init__(bare=bare)
        self._tether = Tether(self)

    def onSettingsChange(self : Self) -> None:
        if self._tether is not None:
            self._tether.onSettingsChange()

    def onPositionChange(self : Self, pos : QPointF) -> None:
        self._tether.onPositionChange(pos)

    def onSelectionChange(self : Self, selected : bool) -> None:
        self._tether.setVisible(selected)
        if selected:
            if not self._tether.cleat().grip().isVisible():
                self._cleat_shown = True
                self._tether.cleat().grip().setVisible(True)
        else:
            if self._cleat_shown:
                self._cleat_shown = False
                self._tether.cleat().grip().setVisible(False)

    def setOriginAPName(self : Self, name : str) -> None:
        """Override to update tether line."""
        super().setOriginAPName(name)
        # parent to origin anchor point
        self._tether.setParentItem(self._origin)
        self._tether.onPositionChange(self.pos())

    def getCleatAPName(self : Self) -> str:
        parent = self.parentItem()
        if parent is None:
            return self._cleat  # workaround for deserialization
        elif isinstance(parent, AnchorPoint):
            return parent.name()
        else:
            logger().error(f"Parent is not an AnchorPoint: {type(parent).__name__}")
            return "Undefined"

    def setCleatAPName(self : Self, name : str) -> None:
        self._cleat = name
        parent = self.parentItem()
        if parent is None:  # handle deserialization
            return
        if isinstance(parent, AnchorPoint):
            grandparent = parent.parentItem()
            if isinstance(grandparent, ItemAnchorPointsMixin):
                self.setParentItem(grandparent.getAnchorPoint(name))
            else:
                logger().error(f"Grandparent is not an ItemAnchorPointsMixin: {type(grandparent).__name__}")
            parent.setName(name)
        else:
            logger().error(f"Parent is not an AnchorPoint: {type(parent).__name__}")

    def compensateRotation(self : Self) -> None:
        rect = self.boundingRect()
        self.setTransformOriginPoint(rect.center())
        if 135 < self.sceneRotation() <= 225:
            self.setRotation((self.rotation() + 180) % 360)
            # counter rotate anchor points
            for ap in self._anchor_points.values():
                ap.setTransformOriginPoint(self.mapToItem(ap, rect.center()))
                ap.setRotation((ap.rotation() + 180) % 360)
