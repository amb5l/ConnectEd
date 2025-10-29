from typing import Self
from enum   import Enum
from dataclasses import dataclass

from PyQt6.QtCore    import Qt, QPointF
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsSceneMouseEvent, QMenu
from PyQt6.QtGui     import QAction

from ..properties import PropertySpec, PropertiesMixin

from ..items.anchor_point import AnchorPoint

from .base_text   import BaseText
from .tether_text import TetherText

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.drawing import DrawingView


class PropertyDisplay(Enum):
    VALUE      = "Value"
    NAME_VALUE = "Name:Value"


class PropertyText(TetherText):
    # class attributes
    _PROPERTY_SPECS_PROPERTY = \
        {
            "Name" : PropertySpec(
                type_name = "str",
                getter    = lambda self: self.name(),
                setter    = lambda self, value: self.setName(value)
            ),
            "Display" : PropertySpec(
                type_name = "PropertyDisplay",
                getter    = lambda self: self.display(),
                setter    = lambda self, value: self.setDisplay(value)
            )
        }
    _PROPERTY_SPECS = \
        TetherText._PROPERTY_SPECS_CLEAT | \
        BaseText._PROPERTY_SPECS_ORIGIN | \
        BaseText._PROPERTY_SPECS_POS | \
        _PROPERTY_SPECS_PROPERTY | \
        BaseText._PROPERTY_SPECS_APPEARANCE

    # instance attributes
    _name    : str
    _display : PropertyDisplay

    def __init__(self : Self, bare : bool = False) -> None:
        super().__init__(bare=bare)
        self._name = "?"
        self._display = PropertyDisplay.VALUE

    def mouseDoubleClickEvent(self : Self, event : QGraphicsSceneMouseEvent) -> None:
        """Handle double-click events to open the edit dialog."""
        if event.button() == Qt.MouseButton.LeftButton:
            from ..views.drawing import getView
            view : "DrawingView" = getView(event.screenPos())
            # workaround for Qt event routing bug
            scene = self.scene()
            if scene:
                item_at_pos = scene.itemAt(event.scenePos(), view.transform())
                if item_at_pos is not None and item_at_pos != self:
                    item_at_pos.mouseDoubleClickEvent(event)
                    return
            view.editPropertyText()
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
        self.onGeometryChange()

    def setParentItem(self : Self, parent : QGraphicsItem) -> None:
        super().setParentItem(parent)
        self.onTextChange()

    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        return [
            view.action("Edit...", view.ui.editPropertyText),
            view.separator(),
            view.action("Appearance...", lambda: view.ui.editAppearance(self)),
            view.action("Properties...", lambda: view.ui.editProperties(self))
        ]

    def parent(self : Self) -> PropertiesMixin:
        p = self.parentItem()
        return \
            self.scene() if p is None else \
            p.parentItem() if isinstance(p, AnchorPoint) else \
            p

    def name(self : Self) -> str:
        return self._name

    def setName(self : Self, value : str) -> None:
        self._name = value
        self.onTextChange()

    def value(self : Self) -> str:
        parent = self.parent()
        return "" if parent is None else parent.getPropertyValue(self._name)

    def setValue(self : Self, value : str) -> None:
        self.parent().setPropertyValue(self._name, value)
        self.onTextChange()

    def display(self : Self) -> PropertyDisplay:
        return self._display

    def setDisplay(self : Self, value : PropertyDisplay) -> None:
        self._display = value
        self.onTextChange()


@dataclass
class PropertyTextSpec:
    anchor  : str
    pos     : QPointF
    cleat   : str
    display : PropertyDisplay = PropertyDisplay.VALUE
    _class  : type = PropertyText
