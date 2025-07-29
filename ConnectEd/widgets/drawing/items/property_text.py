__all__ = ["PropertyDisplay", "PropertyText"]

from typing import Self
from enum   import Enum

from PyQt6.QtCore    import Qt, QPointF
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsSceneMouseEvent

from ..properties import PropertySpec

from . import KPLoc, Quill

from .tether_text import TetherText

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingView


class PropertyDisplay(Enum):
    VALUE      = "Value"
    NAME_VALUE = "Name:Value"

class PropertyText(TetherText):
    # class variables
    _PROPERTY_SPECS_PROPERTY = \
        {
            "Name" : PropertySpec(
                type_name = "str",
                exists    = lambda self: True,
                getter    = lambda self: self.name(),
                setter    = lambda self, value: self.setName(value)
            ),
            "Display" : PropertySpec(
                type_name = "PropertyDisplay",
                exists    = lambda self: True,
                getter    = lambda self: self.display(),
                setter    = lambda self, value: self.setDisplay(value)
            )
        }
    _PROPERTY_SPECS = \
        TetherText._PROPERTY_SPECS_POS | \
        _PROPERTY_SPECS_PROPERTY | \
        TetherText._PROPERTY_SPECS_APPEARANCE

    # instance variables
    _name    : str
    _display : PropertyDisplay

    def __init__(
        self    : Self,
        name    : str = "",
        display : PropertyDisplay = PropertyDisplay.VALUE,
        pos     : QPointF = QPointF(0, 0),
        anchor  : KPLoc = KPLoc.TOP_LEFT,
        bare    : bool = False
    ) -> None:
        self._name    = name
        self._display = display
        super().__init__("", pos, anchor, bare)
        self.onTextChange()

    def mouseDoubleClickEvent(self : Self, event : QGraphicsSceneMouseEvent) -> None:
        """Handle double-click events to open the edit dialog."""
        if event.button() == Qt.MouseButton.LeftButton:
            from .. import getView
            view = getView(event.screenPos())
            # workaround for Qt event routing bug
            scene = self.scene()
            if scene:
                item_at_pos = scene.itemAt(event.scenePos(), view.transform())
                if item_at_pos is not None and item_at_pos != self:
                    item_at_pos.mouseDoubleClickEvent(event)
                    return
            view.editPropertyText(self)
        super().mouseDoubleClickEvent(event)

    def onTextChange(self : Self) -> None:
        text_to_set = ""
        value = self.value()
        match self._display:
            case PropertyDisplay.VALUE:
                text_to_set = f"<{self._name}>" if value == "" else value
            case PropertyDisplay.NAME_VALUE:
                text_to_set = f"{self._name}: {value}"
        super().setText(text_to_set)
        self.onSizeChange()

    def setParentItem(self : Self, parent : QGraphicsItem) -> None:
        super().setParentItem(parent)
        self.onTextChange()

    def getMenuItems(self : Self) -> list[str]:
        return ["Edit..."]

    def setPropertyValue(self : Self, name : str, value : str) -> None:
        if name == self._name:
            self.onTextChange()

    def name(self : Self) -> str:
        return self._name

    def setName(self : Self, value : str) -> None:
        self._name = value
        self.onTextChange()

    def display(self : Self) -> PropertyDisplay:
        return self._display

    def setDisplay(self : Self, value : PropertyDisplay) -> None:
        self._display = value
        self.onTextChange()

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

    def clone(self : Self) -> Self:
        """Create a clone of this PropertyText with a new UUID."""
        clone = PropertyText(
            name    = self.name(),
            display = self.display(),
            pos     = self.pos(),
            anchor  = self._anchor()
         )
        clone.quill = Quill(
            clone, self.quill.getPref()
        )
        return clone

    def ctxMenuEdit(
        self    : Self,
        checked : bool,
        view    : "DrawingView"
    ) -> None:
        view.editPropertyText(self)
