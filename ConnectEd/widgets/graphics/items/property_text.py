from typing      import Self, Any

from PyQt6.QtCore    import Qt, QPointF, QXmlStreamWriter
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsLineItem, \
                            QGraphicsSceneMouseEvent, QMenu
from PyQt6.QtGui     import QAction

from ....app import settings

from ..properties import PropertySpec, PropertiesMixin

from . import NO_CHANGE, ItemType

from .unitext import UniTextItem
from .handle  import HandleItem

from .mixin.origin import ItemOriginMixin
from .mixin.pos    import ItemPosMixin
from .mixin.rotate import ItemRotateMixin
from .mixin.quill  import ItemQuillMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.drawing  import DrawingView
    from ..scenes.drawing import DrawingScene


class TetherItem(QGraphicsLineItem):
    """Tether line between a PropertyText origin and its parent cleat."""

    _item  : "PropertyTextItem"

    def __init__(self : Self, item : "PropertyTextItem", visible : bool = False):
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

    def cleat(self : Self) -> HandleItem | None:
        return self._item.parentItem()

    def toXml(self : Self, xw : QXmlStreamWriter) -> str:
        pass  # no need to serialise


class PropertyTextItem(UniTextItem):
    # class attributes
    _PROPERTIES = \
        {
            "Name" : PropertySpec(
                getter    = lambda self: self.name(),
                setter    = lambda self, value: self.setName(value)
            ),
            "Visible" : PropertySpec(
                type_name = "bool",
                valid     = lambda self: not self.isVisible(),
                getter    = lambda self: self.isVisible(),
                setter    = lambda self, value: self.setVisible(value)
            ),
            "Cleat" : PropertySpec(
                getter    = lambda self: self.getCleat(),
                setter    = lambda self, value: self.setCleat(value)
            )
        } | \
        ItemOriginMixin._PROPERTIES_ORIGIN | \
        ItemPosMixin._PROPERTIES_POS | \
        ItemRotateMixin._PROPERTIES_ROTATE | \
        UniTextItem._PROPERTIES_ALIGN | \
        UniTextItem._PROPERTIES_SIZE | \
        ItemQuillMixin._PROPERTIES_QUILL

    # instance attributes
    _name        : str
    _cleat       : str
    _cleat_shown : bool
    _tether      : TetherItem | None

    def __init__(
        self   : Self,
        name   : str | None           = None,
        cleat  : str | None           = None,
        pos    : QPointF | None       = None,
        origin : str | None           = None,
        fresh  : bool                 = True,
        parent : QGraphicsItem | None = None
    ) -> None:
        super().__init__(fresh=fresh, parent=parent)
        self._tether = TetherItem(self)
        self._name = name
        self.setCleat(cleat)
        if origin is None:
            origin = "Bottom Left" if cleat == "Top Left" else "Top Left"
        self.setOrigin(origin)
        self.setPos(pos or QPointF(0, 0))
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
        self.onTextChange()

    def onPositionChange(
        self : Self,
        pos  : QPointF | None = None
    ) -> None:
        ItemPosMixin.onPositionChange(self, pos)
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

    def onTextChange(self : Self) -> None:
        super().setText(self.value())

    def settingsName(self : Self) -> str:
        item = self.item()
        if item is not None:
            settings_name = f"{item.settingsName()}{self._name}"
            settings_items = settings().get("theme/items")
            if settings_name in vars(settings_items).keys():
                return settings_name
        return "PropertyText"

    def cleat(self : Self) -> str | None:
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
        ItemOriginMixin.setOrigin(self, name)
        if hasattr(self, "_tether"):
            self._tether.setParentItem(self.getHandle(name))
            self._tether.onPositionChange(self.pos())

    def item(self : Self) -> "ItemType | None":
        h : "HandleItem" = self.parentItem()
        return None if h is None else h.parentItem()

    def owner(self : Self) -> PropertiesMixin | None:
        return self.scene() if self.parentItem() is None else self.item()

    def name(self : Self) -> str:
        return self._name

    def setName(self : Self, name : str) -> None:
        self._name = name
        self.onTextChange()

    def value(self : Self) -> Any:
        return f"<{self.name()}>" if self.owner() is None else \
            self.owner().getPropertyValue(self._name, self.onTextChange)

    def setValue(self : Self, value : Any) -> None:
        if value is NO_CHANGE:
            return
        self.owner().setPropertyValue(self._name, value)

    def paint(self, painter, option, widget) -> None:
        from PyQt6.QtGui import QPen
        super().paint(painter, option, widget)
        painter.setPen(QPen(Qt.GlobalColor.yellow, 0))
        painter.drawEllipse(QPointF(0, 0), 1, 1)
        painter.drawLine(QPointF(-1,-1), QPointF(1,1))
        painter.drawLine(QPointF(1,-1), QPointF(-1,1))

    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        items = [
            view.action("Edit...", lambda: view.ui.editPropertyTextDialog(self)),
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
