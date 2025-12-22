from typing      import Self
from dataclasses import dataclass

from PyQt6.QtCore    import Qt, QPointF, QXmlStreamWriter
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsLineItem, \
                            QGraphicsSceneMouseEvent, QMenu
from PyQt6.QtGui     import QAction

from ....app import settings

from ..property   import PropertySpec
from ..properties import PropertiesMixin

from .base_text import BaseTextLine, BaseTextBlock
from .handle    import Handle

from .mixin.pos_rot import ItemPosRotMixin
from .mixin.quill   import ItemQuillMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.drawing  import DrawingView
    from ..scenes.drawing import DrawingScene


class Tether(QGraphicsLineItem):
    """Tether line between a PropertyText origin and its parent cleat."""

    _item  : "PropertyTextMixin"

    def __init__(self : Self, item : "PropertyTextMixin", visible : bool = False):
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

    def onPositionChange(self : Self, _ : QPointF | None = None) -> None:
        if self.cleat() is None:
            return
        line = self.line()
        line.setP2(self.mapFromItem(self.cleat(), QPointF(0, 0)))
        self.setLine(line)

    def cleat(self : Self) -> Handle | None:
        return self._item.parentItem()

    def toXml(self : Self, xw : QXmlStreamWriter) -> str:
        pass  # no need to serialise


class PropertyTextMixin:
    # class attributes
    _PROPERTY_SPECS_NAME = \
        {
            "Property" : PropertySpec(
                getter = lambda self: self.property(),
                setter = lambda self, value: self.setProperty(value)
            )
        }
    _PROPERTY_SPECS_VISIBLE = \
        {
            "Visible" : PropertySpec(
                kind   = "bool",
                valid  = lambda self: not self.isVisible(),
                getter = lambda self: self.isVisible(),
                setter = lambda self, value: self.setVisible(value)
            )
        }
    _PROPERTY_SPECS_CLEAT = \
        {
            "Cleat" : PropertySpec(
                getter = lambda self: self.getCleat(),
                setter = lambda self, value: self.setCleat(value)
            )
        }

    # instance attributes
    _property    : str
    _cleat       : str
    _cleat_shown : bool
    _tether      : Tether | None

    def __init__(
        self     : Self | BaseTextLine | BaseTextBlock,
        property : str | None = None,
        cleat    : str | None = None,
        pos      : QPointF | None = None,
        origin   : str | None = None,
        bare     : bool = False
    ) -> None:
        super().__init__(bare=bare)
        self._tether = Tether(self)
        self._property = property
        self.setCleat(cleat)
        if origin is None:
            origin = "Bottom Left" if cleat == "Top Left" else "Top Left"
        self.setOrigin(origin)
        if pos is None:
            pos = QPointF(0, 0)
        self.setPos(pos)
        self._cleat_shown = False

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
        self.onSettingsChange()

    def onParentChange(self : Self, _parent : QGraphicsItem | None) -> None:
        self.onPropertyChange()

    def onPositionChange(
        self : Self,
        pos  : QPointF | None = None
    ) -> None:
        ItemPosRotMixin.onPositionChange(self, pos)
        if hasattr(self, "_tether"):
            self._tether.onPositionChange(pos)

    def onSelectionChange(self : Self, selected : bool) -> None:
        if self._cleat is None or self._cleat == "":
            return
        cleat_valid = self._cleat is not None and self._cleat != ""
        self._tether.setVisible(selected and cleat_valid)
        self._cleat_shown = selected and cleat_valid
        self._tether.cleat().grip().setVisible(selected and cleat_valid)

    def onSettingsChange(self : Self) -> None:
        super().onSettingsChange()
        if hasattr(self, "_tether"):
            self._tether.onSettingsChange()

    def onSceneRotationChange(self : Self) -> None:
        """Rotation compensation not currently supported."""
        pass

    def onPropertyChange(self : Self) -> None:
        value = self.value()
        text = f"<{self.property()}>" if value == "" else value
        super().setText(text)

    def settingsName(self : Self) -> str:
        item = self.item()
        if item is not None:
            item_name = item.__class__.__name__
            settings_name = f"{item_name}{self._property}"
            settings_items = settings().get("theme/items")
            if settings_name in vars(settings_items).keys():
                return settings_name
        return "PropertyText"

    def getCleat(self : Self) -> str | None:
        return self._cleat

    def setCleat(self : Self, name : str) -> None:
        self._cleat = name
        handle = self.parentItem()
        if handle is None:
            return
        handler = handle.parentItem()  # item or scene with handles
        self.setParentItem(handler.getHandle(name))

    def setOrigin(self : Self, name : str) -> None:
        """Override to update tether line."""
        ItemPosRotMixin.setOrigin(self, name)
        if hasattr(self, "_tether"):
            self._tether.setParentItem(self.getHandle(name))
            self._tether.onPositionChange(self.pos())

    def item(self : Self) -> "PropertiesMixin | None":
        h : "Handle" = self.parentItem()
        return None if h is None else h.parentItem()

    def property(self : Self) -> str:
        return self._property

    def setProperty(self : Self, property : str) -> None:
        self._property = property
        self.onPropertyChange()

    def value(self : Self) -> str:
        source = self.scene() if self.parentItem() is None else self.item()
        if source is None:
            return ""
        return str(source.properties[self._property].get())

    def setValue(self : Self, value : str) -> None:
        source = self.scene() if self.parentItem() is None else self.item()
        source.properties[self._property].set(value)

    def paint(self, painter, option, widget) -> None:
        from PyQt6.QtGui import QPen
        super().paint(painter, option, widget)
        painter.setPen(QPen(Qt.GlobalColor.yellow, 0))
        painter.drawEllipse(QPointF(0, 0), 1, 1)
        painter.drawLine(QPointF(-1,-1), QPointF(1,1))
        painter.drawLine(QPointF(1,-1), QPointF(-1,1))


class PropertyTextLine(PropertyTextMixin, BaseTextLine):
    """Property text as a single line with rotation support."""

    # class attributes
    _PROPERTY_SPECS = \
        PropertyTextMixin._PROPERTY_SPECS_NAME | \
        PropertyTextMixin._PROPERTY_SPECS_VISIBLE | \
        PropertyTextMixin._PROPERTY_SPECS_CLEAT | \
        ItemPosRotMixin._PROPERTY_SPECS_POS_ROT | \
        ItemQuillMixin._PROPERTY_SPECS_QUILL

    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        items = [
            view.action("Edit...", lambda: view.ui.editPropertyText(self)),
            view.separator(),
            view.action("Appearance...", lambda: view.ui.editAppearance(self)),
            view.action("Properties...", lambda: view.ui.editItemProperties(self))
        ]
        return items


class PropertyTextBlock(PropertyTextMixin, BaseTextBlock):
    """Property text as a multi-line block without rotation."""

    # class attributes
    _PROPERTY_SPECS = \
        PropertyTextMixin._PROPERTY_SPECS_NAME | \
        PropertyTextMixin._PROPERTY_SPECS_VISIBLE | \
        PropertyTextMixin._PROPERTY_SPECS_CLEAT | \
        ItemPosRotMixin._PROPERTY_SPECS_POS_ROT | \
        BaseTextBlock._PROPERTY_SPECS_SIZE | \
        ItemQuillMixin._PROPERTY_SPECS_QUILL

    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        items = [
            view.action("Edit...", lambda: view.ui.editPropertyText(self)),
            view.separator(),
            view.action(
                "Auto Width",
                lambda: self.setWidth(
                    self.boundingRect().width() if self._width is None else None
                ),
                self._width is None
            ),
            view.action(
                "Auto Height",
                lambda: self.setHeight(
                    self.boundingRect().height() if self._height is None else None
                ),
                self._height is None
            ),
            view.separator(),
            view.action("Appearance...", lambda: view.ui.editAppearance(self)),
            view.action("Properties...", lambda: view.ui.editItemProperties(self))
        ]
        return items


@dataclass
class PropertyTextSpec:
    anchor  : str
    pos     : QPointF | None = None
    origin  : str | None = None
    block   : bool = False
