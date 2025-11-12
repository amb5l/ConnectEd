from typing import Self
from enum   import Enum
from dataclasses import dataclass

from PyQt6.QtCore    import Qt, QPointF, QXmlStreamWriter
from PyQt6.QtWidgets import QGraphicsItem, \
                            QGraphicsSimpleTextItem, QGraphicsLineItem, \
                            QGraphicsSceneMouseEvent, QMenu
from PyQt6.QtGui     import QAction

from ....app import settings, logger

from .base_text import BaseText
from .handle    import Handle

from .mixin.handle     import ItemHandlesMixin
from .mixin.properties import ItemPropertiesMixin, ItemPropertySpec

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.drawing  import DrawingView
    from ..scenes.drawing import DrawingScene


class PropertyDisplay(Enum):
    VALUE      = "Value"
    NAME_VALUE = "Name:Value"


class Tether(QGraphicsLineItem):
    """Tether line between a PropertyText origin and its parent cleat."""

    _item  : "PropertyText"

    def __init__(self : Self, item : "PropertyText", visible : bool = False):
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

    def cleat(self : Self) -> Handle | None:
        return self._item.parentItem()

    def toXml(self : Self, xw : QXmlStreamWriter) -> str:
        pass  # no need to serialise


class PropertyText(BaseText):
    # class attributes
    _PROPERTY_SPECS_PROPERTY = \
        {
            "Name" : ItemPropertySpec(
                type_name = "str",
                getter    = lambda self: self.name(),
                setter    = lambda self, value: self.setName(value)
            ),
            "Display" : ItemPropertySpec(
                type_name = "PropertyDisplay",
                getter    = lambda self: self.display(),
                setter    = lambda self, value: self.setDisplay(value)
            )
        }
    _PROPERTY_SPECS = \
        {
            "Cleat" : ItemPropertySpec(
                type_name = "str",
                getter    = lambda self: self.getCleat(),
                setter    = lambda self, value: self.setCleat(value)
            )
        } | \
        BaseText._PROPERTY_SPECS_ORIGIN | \
        BaseText._PROPERTY_SPECS_POS | \
        _PROPERTY_SPECS_PROPERTY | \
        BaseText._PROPERTY_SPECS_APPEARANCE

    # instance attributes
    _name        : str
    _cleat       : str | None
    _cleat_shown : bool
    _display     : PropertyDisplay
    _tether      : Tether | None

    def __init__(
        self     : Self,
        name     : str | None = None,
        cleat    : str | None = None,
        pos      : QPointF | None = None,
        origin   : str | None = None,
        display  : PropertyDisplay = PropertyDisplay.VALUE,
        bare     : bool = False
    ) -> None:
        self._name        = name
        self._cleat       = None
        self._cleat_shown = False
        self._display     = PropertyDisplay.VALUE
        self._tether      = None
        super().__init__(bare=bare)
        self._tether = Tether(self)

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

    def onSceneChange(self : Self, _scene : "DrawingScene | None") -> None:
        self.onTextChange()

    def onParentChange(self : Self, _parent : QGraphicsItem) -> None:
        self.onSettingsChange()

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

    def onSettingsChange(self : Self) -> None:
        if self._tether is not None:
            self._tether.onSettingsChange()
        super().onSettingsChange()

    def onRotationChange(self : Self) -> None:
        """Rotation compensation."""
        rect = self.boundingRect()
        self.setTransformOriginPoint(rect.center())
        if 135 < self.sceneRotation() <= 225:
            # Use base class to prevent recursion
            QGraphicsSimpleTextItem.setRotation(self, (self.rotation() + 180) % 360)
            # counter rotate handles
            for h in self._handles.values():
                h.setTransformOriginPoint(self.mapToItem(h, rect.center()))
                QGraphicsSimpleTextItem.setRotation(h, (h.rotation() + 180) % 360)

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

    def getCleat(self : Self) -> str:
        parent = self.parentItem()
        if parent is None:
            return self._cleat  # workaround for deserialization
        elif isinstance(parent, Handle):
            return parent.name()
        else:
            logger().error(f"Parent is not a Handle: {type(parent).__name__}")
            return "Undefined"

    def setCleat(self : Self, name : str) -> None:
        self._cleat = name
        parent = self.parentItem()
        if parent is None:  # handle deserialization
            return
        if isinstance(parent, Handle):
            grandparent = parent.parentItem()
            if isinstance(grandparent, ItemHandlesMixin):
                self.setParentItem(grandparent.getHandle(name))
            else:
                logger().error(f"Grandparent is not an ItemHandleMixin: {type(grandparent).__name__}")
            parent.setName(name)
        else:
            logger().error(f"Parent is not a Handle: {type(parent).__name__}")

    def setOrigin(self : Self, name : str) -> None:
        """Override to update tether line."""
        super().setOrigin(name)
        self._tether.setParentItem(self._origin)
        self._tether.onPositionChange(self.pos())

    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        return [
            view.action("Edit...", view.ui.editPropertyText),
            view.separator(),
            view.action("Appearance...", lambda: view.ui.editAppearance(self)),
            view.action("Properties...", lambda: view.ui.editItemProperties(self))
        ]

    def item(self : Self) -> "ItemPropertiesMixin | None":
        h : "Handle" = self.parentItem()
        return None if h is None else h.parentItem()

    def name(self : Self) -> str:
        return self._name

    def setName(self : Self, name : str) -> None:
        self._name = name
        self.onTextChange()

    def value(self : Self) -> str:
        return str(self.item().properties[self._name].get()) if self.item() else ""

    def setValue(self : Self, value : str) -> None:
        self.item().properties[self._name].set(value)
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
