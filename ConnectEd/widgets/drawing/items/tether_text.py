__all__ = ["Tether","TetherText"]

from typing import Self, Optional

from PyQt6.QtCore    import QPointF, QRectF
from PyQt6.QtWidgets import QWidget, QGraphicsItem, QStyleOptionGraphicsItem
from PyQt6.QtGui     import QPainter

from . import ElementMixin, TextColorFont,\
              AttrSpec, KP, KPManager

from .base_text import BaseText


class Tether(QGraphicsItem):
    """Tether line between a TetherText anchor and its parent cleat."""

    _item: "TetherText"

    def __init__(self, item: "TetherText"):
        super().__init__(item)  # Parent it to the Property
        self._item = item
        self.setZValue(-1)  # Draw behind the property text
        self.setVisible(False)  # Initially hidden

    def boundingRect(self) -> QRectF:
        parent : Optional[ElementMixin] = self._item.parentItem()
        if not parent:
            return QRectF()
        anchor_pos = self._item._kpm.anchor_offset
        cleat_pos_parent = parent._kpm.key_points[self._item._cleat].pos()
        cleat_pos_local = self._item.mapFromParent(cleat_pos_parent)
        rect = QRectF(anchor_pos, cleat_pos_local).normalized()
        return rect.adjusted(-5, -5, 5, 5)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget) -> None:
        if not self._item:
            return
        parent = self._item.parentItem()
        if not parent:
            return
        anchor_pos = self._item._kpm.anchor_offset
        cleat_pos_parent = parent._kpm.key_points[self._item._cleat].pos()
        cleat_pos_local = self._item.mapFromParent(cleat_pos_parent)
        painter.setPen(self._item.appearance.outline.pen)
        painter.drawLine(anchor_pos, cleat_pos_local)

# Understanding positioning:
# 1. TetherText pos is offset from cleat pos to TetherText anchor
# 2. cleat pos is relative to parent top left
# 3. TetherText anchor offset is relative to TetherText top left
# So when a TetherText pos is specified, the cleat pos is added,
# and then anchor offset is subtracted.
# This cleat-to-anchor pos is stored in _pos. Useful for cleat (keypoint) moves.

class TetherText(BaseText):
    # class variables
    _ATTR_SPECS_BASIC = [
        AttrSpec(
            name      = "Cleat",
            type_name = "KP",
            exists    = lambda self: True,
            getter    = lambda self: self.cleat(),
            setter    = lambda self, value: self.setCleat(value)
        )
    ] + BaseText._ATTR_SPECS_BASIC
    _ATTR_SPECS = \
        _ATTR_SPECS_BASIC + \
        BaseText._ATTR_SPECS_TEXT + \
        BaseText._ATTR_SPECS_APPEARANCE_TEXT

    # instance variables
    _cleat   : KP
    _pos     : QPointF
    _tether  : Optional[Tether]

    def __init__(
        self    : Self,
        pos     : QPointF = QPointF(0, 0),
        anchor  : KP = KP.TOP_LEFT,
        cleat   : KP = KP.BOTTOM_LEFT,
        bare    : bool = False
    ) -> None:
        super().__init__("", pos, anchor, bare)
        self._pos    = pos
        self._cleat  = cleat
        self._tether = None
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable , True)

    def setPos(self : Self, pos : QPointF) -> None:
        """Set offset from parent cleat to my anchor."""
        self._pos = pos
        parent : Optional[ElementMixin] = self.parentItem()
        if parent is not None and hasattr(parent, '_kpm') and parent._kpm is not None:
            parent_kpm : KPManager = parent._kpm
            # cleat position is relative to parent top left
            cleat_pos = parent_kpm.key_points[self._cleat].pos()
        else:
            cleat_pos = QPointF(0, 0)
        anchor_pos = pos + cleat_pos
        super().setPos(anchor_pos)

    def setPosX(self : Self, value : float) -> None:
        self.setPos(QPointF(value, self._pos.y()))

    def setPosY(self : Self, value : float) -> None:
        self.setPos(QPointF(self._pos.x(), value))

    def pos(self : Self) -> QPointF:
        return self._pos

    def updatePos(self : Self) -> None:
        self.setPos(self._pos)

    def cleat(self : Self) -> KP:
        return self._cleat

    def setCleat(self : Self, cleat : KP) -> None:
        self._cleat = cleat
        self.setPos(self._pos)

    def _connectToKPMSignals(self : Self) -> None:
        """Connect to parent element's KPManager signals."""
        parent : Optional[ElementMixin] = self.parentItem()
        if parent is not None and hasattr(parent, '_kpm') and parent._kpm is not None:
            parent._kpm.change.connect(self.updatePos)

    def _disconnectFromKPMSignals(self : Self) -> None:
        """Disconnect from parent element's KPManager signals."""
        parent : Optional[ElementMixin] = self.parentItem()
        if parent is not None and hasattr(parent, '_kpm') and parent._kpm is not None:
            parent._kpm.change.disconnect(self.updatePos)

    def _createTether(self) -> None:
        """Create the tether line child item if it doesn't exist."""
        if self._tether is None:
            self._tether = Tether(self)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        """Override to detect when parented and connect to parent signals."""
        result = super().itemChange(change, value)
        if change == QGraphicsItem.GraphicsItemChange.ItemParentHasChanged:
            if value is None:
                self._disconnectFromKPMSignals()
            else:
                self._connectToKPMSignals()
            self.setPos(self._pos)
        elif change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            parent = self.parentItem()
            if parent is not None:
                parent_kpm = parent._kpm
                cleat_pos = parent_kpm.key_points[self._cleat].pos()
                anchor_pos = value + self._kpm.anchor_offset
                self._pos = anchor_pos - cleat_pos
        elif change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            self._createTether()
            if self._tether:
                self._tether.setVisible(self.isSelected())
        return result

    def clone(self : Self) -> Self:
        """Create a clone of this TetherText with a new UUID."""
        clone = TetherText(self.pos(), self.anchor(), self.cleat())
        clone.appearance.text = TextColorFont(
            clone, self.appearance.text.getPref()
        )
        return clone
