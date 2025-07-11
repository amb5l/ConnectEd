__all__ = ["PropertyDisplay", "PropertyText", "Tether"]

from typing import Self, Optional
from enum   import Enum

from PyQt6.QtCore    import Qt, QPointF, QRectF
from PyQt6.QtWidgets import QWidget, QStyleOptionGraphicsItem, QGraphicsItem, \
                            QGraphicsSceneMouseEvent
from PyQt6.QtGui     import QPainter
from PyQt6.QtGui     import QPainterPath

from . import ElementMixin, AttrSpec, KPManager, KP, TextColorFont

from .base_text_line import BaseTextLine

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingView


class PropertyDisplay(Enum):
    VALUE      = "Value"
    NAME_VALUE = "Name:Value"

class Tether(QGraphicsItem):
    """Tether line between a property's anchorand its parent cleat."""

    _property: "PropertyText"

    def __init__(self, property: "PropertyText"):
        super().__init__(property)  # Parent it to the Property
        self._property = property
        self.setZValue(-1)  # Draw behind the property text
        self.setVisible(False)  # Initially hidden

    def boundingRect(self) -> QRectF:
        if not self._property:
            return QRectF()
        parent = self._property.parentItem()
        if not parent:
            return QRectF()
        anchor_pos = self._property._kpm.anchor_offset
        cleat_pos_parent = parent._kpm.key_points[self._property._cleat].pos()
        cleat_pos_local = self._property.mapFromParent(cleat_pos_parent)
        rect = QRectF(anchor_pos, cleat_pos_local).normalized()
        return rect.adjusted(-5, -5, 5, 5)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget) -> None:
        if not self._property:
            return
        parent = self._property.parentItem()
        if not parent:
            return
        anchor_pos = self._property._kpm.anchor_offset
        cleat_pos_parent = parent._kpm.key_points[self._property._cleat].pos()
        cleat_pos_local = self._property.mapFromParent(cleat_pos_parent)
        painter.setPen(self._property.appearance.outline.pen)
        painter.drawLine(anchor_pos, cleat_pos_local)

# Understanding positioning:
# 1. PropertyText pos is offset from cleat pos to PropertyText anchor
# 2. cleat pos is relative to parent top left
# 3. PropertyText anchor offset is relative to PropertyText top left
# So when a PropertyText pos is specified, the cleat pos is added,
# and then anchor offset is subtracted.
# This cleat-to-anchor pos is stored in _pos. Useful for cleat (keypoint) moves.

class PropertyText(BaseTextLine):
    # class variables
    _ATTR_SPECS = ElementMixin._ATTR_SPECS + [
        AttrSpec(
            name      = "Cleat",
            type_name = "KP",
            exists    = lambda self: True,
            getter    = lambda self: self.cleat(),
            setter    = lambda self, value: self.setCleat(value)
        ),
        AttrSpec(
            name      = "Anchor",
            type_name = "KP",
            exists    = lambda self: True,
            getter    = lambda self: self.anchor(),
            setter    = lambda self, value: self.setAnchor(value)
        ),
        AttrSpec(
            name      = "Name",
            type_name = "str",
            exists    = lambda self: True,
            getter    = lambda self: self.name(),
            setter    = lambda self, value: self.setName(value)
        ),
        AttrSpec(
            name      = "Display",
            type_name = "PropertyDisplay",
            exists    = lambda self: True,
            getter    = lambda self: self.display(),
            setter    = lambda self, value: self.setDisplay(value)
        )
    ] + ElementMixin._ATTR_SPECS_TEXT
    _MENU_ITEM_NAMES = ["Edit"]

    # instance variables
    _name    : str
    _display : PropertyDisplay
    _cleat   : KP
    _pos     : QPointF
    _tether  : Optional[Tether]
    _cache   : str              # value cache

    def __init__(
        self    : Self,
        name    : str = "",
        display : PropertyDisplay = PropertyDisplay.VALUE,
        pos     : QPointF = QPointF(0, 0),
        anchor  : KP = KP.TOP_LEFT,
        cleat   : KP = KP.BOTTOM_LEFT,
        bare    : bool = False
    ) -> None:
        super().__init__(text="", pos=pos, anchor=anchor)
        self._name = name
        self._display = display
        self._cleat = cleat
        self._tether = None
        self._cache = ""
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable , True)
        self.refresh()

    def mouseDoubleClickEvent(self : Self, event : QGraphicsSceneMouseEvent) -> None:
        """Handle double-click events to open the edit dialog."""
        if event.button() == Qt.MouseButton.LeftButton:
            # Fix for Qt event routing bug
            from .. import getView
            view = getView(event.screenPos())
            scene = self.scene()
            if scene:
                item_at_pos = scene.itemAt(event.scenePos(), view.transform())
                if item_at_pos != self:
                    item_at_pos.mouseDoubleClickEvent(event)
                    return
            view.editPropertyText(self)
        super().mouseDoubleClickEvent(event)

    def onPropertyChanged(self : Self, name : str, value : str) -> None:
        """Handle property value change signal from parent."""
        if name == self._name:
            self._cache = value
            self.refresh()

    def onPropertyDeleted(self : Self, name : str) -> None:
        """Handle property deletion signal from parent."""
        if name == self._name:
            self._cache = ""
            self.refresh()

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
        """Update position based on current cleat position."""
        self.setPos(self._pos)

    def name(self : Self) -> str:
        return self._name

    def setName(self : Self, value : str) -> None:
        old_name = self._name
        self._name = value
        parent = self.parentItem()
        if parent is not None and hasattr(parent, 'disconnectFromPropertySignals'):
            if old_name:
                parent.disconnectFromPropertySignals(self)
        self._updateCache()
        self._connectToPropertySignals()
        self.refresh()

    def display(self : Self) -> PropertyDisplay:
        return self._display

    def setDisplay(self : Self, value : PropertyDisplay) -> None:
        self._display = value
        self.refresh()

    def cleat(self : Self) -> KP:
        return self._cleat

    def setCleat(self : Self, cleat : KP) -> None:
        self._cleat = cleat
        self.setPos(self._pos)
        self.update()

    def value(self : Self) -> str:
        parent = self.parentItem()
        if parent is None:
            parent = self.scene()
        if parent is None:
            return ""
        elif hasattr(parent, 'getProperty') and self._name:
            return parent.getProperty(self._name)
        else:
            return ""

    def setValue(self : Self, value : str) -> None:
        parent = self.parentItem()
        if parent is None:
            parent = self.scene()
        if parent is None:
            return
        elif hasattr(parent, 'setProperty') and self._name:
            parent.setProperty(self._name, value)
        else:
            return

    def _updateCache(self : Self) -> None:
        """Update the cached property value from parent."""
        self._cache = self.value()

    def _connectToPropertySignals(self : Self) -> None:
        """Connect to parent element's property signals."""
        parent = self.parentItem()
        if parent is None: # no parent means we get properties from the scene
            self.scene().connectToPropertySignals(self)
        elif hasattr(parent, 'connectToPropertySignals') and self._name:
            parent.connectToPropertySignals(self)

    def _disconnectFromPropertySignals(self : Self) -> None:
        """Disconnect from parent element's property signals."""
        parent = self.parentItem()
        if parent is not None and hasattr(parent, 'disconnectFromPropertySignals'):
            parent.disconnectFromPropertySignals(self)

    def _connectToKPMSignals(self : Self) -> None:
        """Connect to parent element's KPManager signals."""
        parent : Optional[ElementMixin] = self.parentItem()
        if parent is not None and hasattr(parent, '_kpm') and parent._kpm is not None:
            parent._kpm.change.connect(self.updatePos)

    def _createTether(self) -> None:
        """Create the tether line child item if it doesn't exist."""
        if self._tether is None:
            self._tether = Tether(self)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        """Override to detect when parented and connect to parent signals."""
        result = super().itemChange(change, value)
        if change == QGraphicsItem.GraphicsItemChange.ItemParentHasChanged:
            if value is None: # being removed from parent
                self._disconnectFromPropertySignals()
            else: # being parented
                self._updateCache()
                self._connectToPropertySignals()

            # Property has been parented, connect to parent's KPManager signals
            self._connectToKPMSignals()
            # Recalculate position now that we have a parent
            self.setPos(self._pos)
        elif change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            parent = self.parentItem()
            if parent is not None:
                parent_kpm = parent._kpm
                cleat_pos = parent_kpm.key_points[self._cleat].pos()
                anchor_pos = value + self._kpm.anchor_offset
                self._pos = anchor_pos - cleat_pos
        elif change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            # Selection changed - show/hide tether line
            self._createTether()
            if self._tether:
                self._tether.setVisible(self.isSelected())
        return result

    def paint(
        self    : Self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        # Call parent paint method to draw the text and selection outline
        super().paint(painter, option, widget)

    def setText(self : Self, text : str) -> None:
        raise NotImplementedError("Property.setText is not implemented")

    def refresh(self : Self) -> None:
        text_to_set = ""
        # Use cached value instead of direct property access
        value = self._cache
        match self._display:
            case PropertyDisplay.VALUE:
                text_to_set = f"<{self._name}>" if value == "" else value
            case PropertyDisplay.NAME_VALUE:
                text_to_set = f"{self._name}: {value}"
        super().setText(text_to_set)
        super().update()
        if hasattr(self, "_kpm"):
            self._kpm.updatePositions()
            # Recalculate position now that text has changed
            self.setPos(self._pos)

    def clone(self : Self) -> Self:
        """Create a clone of this property text with a new UUID."""
        clone = PropertyText(
            name    = self.name(),
            display = self.display(),
            pos     = self.pos(),
            anchor  = self.anchor(),
            cleat   = self.cleat()
         )
        clone.appearance.text = TextColorFont(
            clone, self.appearance.text.getPref()
        )
        return clone

    def ctxMenuEdit(
        self    : Self,
        checked : bool,
        view    : "DrawingView"
    ) -> None:
        view.editPropertyText(self)
