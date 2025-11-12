from typing import Self
from enum   import Enum
from dataclasses import dataclass

from PyQt6.QtCore    import Qt, QPointF
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsSceneMouseEvent, QMenu
from PyQt6.QtGui     import QAction

from ....app import settings

from ..properties  import PropertySpec

from .base_text   import BaseText
from .tether_text import TetherText
from .handle      import Handle

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..properties     import PropertiesMixin
    from ..views.drawing  import DrawingView
    from ..scenes.drawing import DrawingScene


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
    _name     : str
    _display  : PropertyDisplay

    def __init__(
        self     : Self,
        name     : str | None = None,
        cleat    : str | None = None,
        pos      : QPointF | None = None,
        origin   : str | None = None,
        display  : PropertyDisplay = PropertyDisplay.VALUE,
        bare     : bool = False
    ) -> None:
        self._name = name
        self._display = PropertyDisplay.VALUE
        super().__init__(bare=bare)
        if bare:
            return
        self.setCleat(cleat)
        if origin is None:
            origin = "Bottom Left" if cleat == "Top Left" else "Top Left"
        self.setOrigin(origin)
        pos = QPointF(0, 0) if pos is None else pos
        self.setPos(pos)
        self.setDisplay(display)

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

    def onSceneChange(self : Self, scene : "DrawingScene | None") -> None:
        self.onTextChange()

    def onParentChange(self : Self, parent : QGraphicsItem) -> None:
        self.onSettingsChange()

    def onTextChange(self : Self) -> None:
        text_to_set = ""
        value = self.value()
        if not hasattr(self, "_display"):
            return
        if self._display == PropertyDisplay.NAME_VALUE:
            text_to_set = f"{self.name()}: {value}"
        else:
            text_to_set = f"<{self.name()}>" if value == "" else value
        super().setText(text_to_set)
        self.onGeometryChange()

    def settingsName(self : Self) -> str:
        item = self.item()
        if item is not None:
            item_name = item.__class__.__name__
            settings_name = f"{item_name}{self._name}"
            settings_items = settings().get("theme/items")
            if settings_name in vars(settings_items).keys():
                return settings_name
        return super().settingsName()

    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        return [
            view.action("Edit...", view.ui.editPropertyText),
            view.separator(),
            view.action("Appearance...", lambda: view.ui.editAppearance(self)),
            view.action("Properties...", lambda: view.ui.editItemProperties(self))
        ]

    def item(self : Self) -> "PropertiesMixin | None":
        h : "Handle" = self.parentItem()
        return None if h is None else h.parentItem()

    def name(self : Self) -> str:
        return self._name

    def setName(self : Self, name : str) -> None:
        self._name = name
        self.onTextChange()

    def value(self : Self) -> str:
        return str(self.item().getPropertyValue(self._name)) if self.item() else ""

    def setValue(self : Self, value : str) -> None:
        self.item().setPropertyValue(self._name, value)
        self.onTextChange()

    def display(self : Self) -> PropertyDisplay:
        return self._display

    def setDisplay(self : Self, value : PropertyDisplay) -> None:
        self._display = value
        self.onTextChange()


@dataclass
class PropertyTextSpec:
    anchor  : str
    pos     : QPointF | None = None
    origin  : str | None = None
    display : PropertyDisplay = PropertyDisplay.VALUE
