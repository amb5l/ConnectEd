from typing import Self, Optional
from enum   import Enum

from PyQt6.QtCore    import QPointF, QRectF
from PyQt6.QtWidgets import QWidget, QStyleOptionGraphicsItem, QGraphicsItem
from PyQt6.QtGui     import QPainter

from ....core import Z_DRAWING

from . import ElementMixin, KPManager, KPLoc, KP, cmdPlaceElement

from .base_text_line import BaseTextLine


class PropertyDisplay(Enum):
    HIDDEN     = "HIDDEN"
    VALUE      = "Value"
    NAME_VALUE = "Name: Value"

class Tether(QGraphicsItem):
    """Tether line between a property's anchorand its parent cleat."""

    _property: "Property"

    def __init__(self, property: "Property"):
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

class Property(BaseTextLine):
    # class variables
    Z = Z_DRAWING
    _XML_ATTRS = ElementMixin._XML_ATTRS | {
        "name"    : "str",
        "value"   : "str",
        "display" : "PropertyDisplay" #  TODO: generic enum support in XML i/o?
    }

    # instance variables
    _name      : str
    _value     : str
    _display   : PropertyDisplay
    _cleat     : KPLoc
    _local_pos : QPointF
    _tether    : Optional[Tether]

    def __init__(
        self    : Self,
        name    : str,
        value   : str,
        display : PropertyDisplay = PropertyDisplay.VALUE,
        pos     : QPointF = QPointF(0, 0),
        anchor  : KPLoc = KP.TOP_LEFT,
        cleat   : KPLoc = KP.BOTTOM_LEFT
    ) -> None:
        super().__init__(text="", pos=pos, anchor=anchor)
        self._name = name
        self._value = value
        self._display = display
        self._tether = None
        # Don't call initElement again - parent already did it
        self.setCleat(cleat)
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable , True)
        self.refresh()

    def setPos(self : Self, pos : QPointF) -> None:
        self._local_pos = pos
        parent : Optional[ElementMixin] = self.parentItem()
        if parent is not None:
            parent_kpm : KPManager = parent._kpm
            cleat_pos = parent_kpm.key_points[self._cleat].pos()
        else:
            cleat_pos = QPointF(0, 0)
        desired_anchor_pos = pos + cleat_pos
        super().setPos(desired_anchor_pos)

    def pos(self : Self) -> QPointF:
        return self._local_pos

    def updatePos(self : Self) -> None:
        """Update position based on current cleat position."""
        self.setPos(self._local_pos)

    @property
    def name(self : Self) -> str:
        return self._name

    @name.setter
    def name(self : Self, value : str) -> None:
        self._name = value
        self.refresh()

    @property
    def value(self : Self) -> str:
        return self._value

    @value.setter
    def value(self : Self, value : str) -> None:
        self._value = value
        self.refresh()

    @property
    def display(self : Self) -> PropertyDisplay:
        return self._display

    @display.setter
    def display(self : Self, value : PropertyDisplay) -> None:
        self._display = value
        self.refresh()

    def setCleat(self : Self, cleat : KPLoc) -> None:
        self._cleat = cleat
        self.update()

    def connectToParentSignals(self : Self) -> None:
        """Connect to parent element's KPManager signals."""
        parent : Optional[ElementMixin] = self.parentItem()
        if parent is not None and hasattr(parent, '_kpm') and parent._kpm is not None:
            parent._kpm.change.connect(self.updatePos)

    def _createTetherLine(self) -> None:
        """Create the tether line child item if it doesn't exist."""
        if self._tether is None:
            self._tether = Tether(self)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        """Override to detect when parented and connect to parent signals."""
        result = super().itemChange(change, value)
        if change == QGraphicsItem.GraphicsItemChange.ItemParentHasChanged:
            # Property has been parented, connect to parent's KPManager signals
            self.connectToParentSignals()
        elif change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            # Selection changed - show/hide tether line
            self._createTetherLine()
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
        match self._display:
            case PropertyDisplay.HIDDEN:
                text_to_set = "<hidden>"
            case PropertyDisplay.VALUE:
                text_to_set = f"<{self._name}>" if self._value == "" else self._value
            case PropertyDisplay.NAME_VALUE:
                text_to_set = f"{self._name}: {self._value}"
        super().setText(text_to_set)
        self.setVisible(self._display != PropertyDisplay.HIDDEN)
        super().update()
        if hasattr(self, "_kpm") and self._display != PropertyDisplay.HIDDEN:
            self._kpm.updatePositions()
            # Recalculate position now that text has changed
            self.setPos(self._local_pos)

class cmdPlaceProperty(cmdPlaceElement):
    element : Property
