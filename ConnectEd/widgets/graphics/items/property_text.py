from typing      import Self, Any

from PyQt6.QtCore    import Qt, QPointF, QXmlStreamWriter
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsLineItem, \
                            QGraphicsSceneMouseEvent, QMenu
from PyQt6.QtGui     import QAction, QColor

from ....app import settings, logger

from ....core.types import Default, DEFAULT, NO_CHANGE, AlignH, AlignV, \
                           HandleId, RectHandleId
from ....core.utils import val2str

from ..properties import InherentProperty, PropertiesMixin

from . import ItemType

from .text   import TextItem
from .handle import HandleItem


from .mixin.origin import ItemOriginMixin
from .mixin.pos    import ItemPosMixin
from .mixin.rotate import ItemRotateMixin
from .mixin.handle import ItemHandlesMixin
from .mixin.quill  import ItemQuillMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.drawing  import DrawingView
    from ..scenes.drawing import DrawingScene


class TetherItem(QGraphicsLineItem):
    """Tether line between a PropertyText origin and its parent cleat."""

    _item  : "PropertyTextItem"

    def __init__(self : Self, item : "PropertyTextItem"):
        self._item = item
        super().__init__(item.getOriginHandle())
        self.setVisible(item.isSelected())
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


class PropertyTextItem(TextItem):
    # class attributes
    _PROPERTIES = \
        {
            "Name" : InherentProperty(
                kind   = "Str",
                getter = lambda self: self.name(),
                setter = lambda self, value: self.setName(value)
            ),
            "Visible" : InherentProperty(
                kind   = "Bool",
                valid  = lambda self: not self.isVisible(),
                getter = lambda self: self.isVisible(),
                setter = lambda self, value: self.setVisible(value)
            ),
            "Cleat" : InherentProperty(
                kind   = lambda self: self.cleatEnumTypeName(),
                getter = lambda self: self.getCleat(),
                setter = lambda self, value: self.setCleat(value)
            )
        } | \
        ItemOriginMixin._PROPERTIES_ORIGIN | \
        ItemPosMixin._PROPERTIES_POS | \
        ItemRotateMixin._PROPERTIES_ROTATE | \
        TextItem._PROPERTIES_ALIGN | \
        TextItem._PROPERTIES_SIZE | \
        ItemQuillMixin._PROPERTIES_QUILL

    # instance attributes
    _name        : str
    _cleat       : HandleId | None
    _cleat_shown : bool
    _tether      : TetherItem | None

    def __init__(
        self   : Self,
        name      : str,
        cleat     : HandleId | None      = None,
        pos       : QPointF | None       = None,
        origin    : RectHandleId         = RectHandleId.TOP_LEFT,
        align_h   : AlignH               = AlignH.LEFT,
        align_v   : AlignV               = AlignV.TOP,
        width     : float                = -1.0,
        height    : float                = -1.0,
        color     : QColor | Default     = DEFAULT,
        family    : str    | Default     = DEFAULT,
        size      : float  | Default     = DEFAULT,
        bold      : bool   | Default     = DEFAULT,
        italic    : bool   | Default     = DEFAULT,
        underline : bool   | Default     = DEFAULT,
        fresh     : bool                 = True,
        parent    : QGraphicsItem | None = None
    ) -> None:
        super().__init__(
            text      = "?",    # uninitialized value
            block     = False,  # default
            rotcomp   = True,   # always True for PropertyTextItem
            pos       = pos,
            origin    = origin,
            align_h   = align_h,
            align_v   = align_v,
            width     = width,
            height    = height,
            color     = color,
            family    = family,
            size      = size,
            bold      = bold,
            italic    = italic,
            underline = underline,
            fresh     = fresh,
            parent    = parent
        )
        self._tether = TetherItem(self)
        self._name = name
        self.setCleat(cleat, parent)
        self._cleat_shown = False
        self.onTextChange()

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
        text = val2str(self.value())
        if text == "":
            text = f"<{self._name}>"
        super().setText(text)

    def settingsName(self : Self) -> str:
        item = self.item()
        if item is not None:
            settings_name = f"{item.settingsName()}{self._name}"
            settings_items = settings().get("theme/items")
            if settings_name in vars(settings_items).keys():
                return settings_name
        return "PropertyText"

    def cleat(self : Self) -> HandleId | None:
        return self._cleat

    def setCleat(
        self   : Self,
        id     : HandleId | None,
        parent : "ItemHandlesMixin | None" = None
    ) -> bool:
        self._cleat = id
        item = parent or self.item()
        if item is None:
            return False
        for child in item.childItems():
            if isinstance(child, HandleItem) and child.id() == id:
                self.setParentItem(child)
                return True
        logger().warning("Cleat not found in parent item")
        return False

    def setOrigin(self : Self, id : RectHandleId) -> None:
        """Override to update tether line."""
        ItemOriginMixin.setOrigin(self,  id)
        if hasattr(self, "_tether"):  # guard against partial initialisation
            self._tether.setParentItem(self.getOriginHandle())
            self._tether.onPositionChange(self.pos())

    def item(self : Self) -> ItemType | None:
        parent = self.parentItem()
        if isinstance(parent, HandleItem):
            return parent.parentItem()
        elif isinstance(parent, ItemType):
            return parent
        elif parent is not None:
            # Only warn for unexpected parent types, not during initialization
            logger().warning(f"Bad parent item ({parent.__class__.__name__})")
        return None

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
                    self.boundingRect().width() if self._width < 0.0 else -1.0
                ),
                self._width < 0.0
            ),
            view.action(
                "Auto Height",
                lambda: self.setHeight(
                    self.boundingRect().height() if self._height < 0.0 else -1.0
                ),
                self._height < 0.0
            ),
            view.separator(),
            view.action("Appearance...", lambda: view.ui.editAppearance(self)),
            view.action("Properties...", lambda: view.ui.editItemProperties(self))
        ]
        return items
