from typing import Self, Any

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QGraphicsItem, QMenu
from PyQt6.QtGui     import QAction

from ....app import settings, logger

from ....core.types import DEFAULT, NO_CHANGE, AlignH, AlignV, \
                           HandleId, RectHandleId, DataKind, \
                           Color, FontFamily, FontSize, FontBool
from ....core.utils import val2str

from ..properties import InherentProperty, PropertiesMixin

from . import ItemType

from .text   import TextItem
from .handle import HandleItem
from .tether import PropertyTextTetherItem


from .mixin.transform import ItemTransformMixin
from .mixin.handle    import ItemHandlesMixin
from .mixin.quill     import ItemQuillMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.drawing  import DrawingView
    from ..scenes.drawing import DrawingScene


class PropertyTextItem(TextItem):
    # class attributes
    _PROPERTIES = \
        {
            "Name" : InherentProperty(
                kind   = DataKind.STR,
                getter = lambda self: self.name(),
                setter = lambda self, value: self.setName(value)
            ),
            "Visible" : InherentProperty(
                kind   = DataKind.BOOL,
                worthy = lambda self: not self.isVisible(),
                getter = lambda self: self.isVisible(),
                setter = lambda self, value: self.setVisible(value)
            ),
            "Cleat" : InherentProperty(
                kind   = lambda self: self.item().handleIdKind(),
                getter = lambda self: self.cleat(),
                setter = lambda self, value: self.setCleat(value)
            )
        } | \
        ItemTransformMixin._PROPERTIES_POS | \
        ItemTransformMixin._PROPERTIES_ROTATE | \
        ItemTransformMixin._PROPERTIES_RECT_ORIGIN | \
        TextItem._PROPERTIES_ALIGN | \
        TextItem._PROPERTIES_SIZE | \
        ItemQuillMixin._PROPERTIES_QUILL

    # instance attributes
    _name   : str
    _cleat  : HandleId | None
    _tether : PropertyTextTetherItem | None

    def settingsName(self : Self) -> str:
        item = self.item()
        if item is not None and hasattr(self, "_name"):
            settings_name = f"{item.settingsName()}{self._name}"
            settings_items = settings().get("theme/items")
            if settings_name in vars(settings_items).keys():
                return settings_name
        return "PropertyText"

    def __init__(
        self      : Self,
        name      : str                  = "",
        cleat     : HandleId | None      = None,
        pos       : QPointF | None       = None,
        rotation  : float                = 0.0,
        mirror_h  : bool                 = False,
        mirror_v  : bool                 = False,
        autoflip  : bool                 = True,
        origin    : RectHandleId         = RectHandleId.TOP_LEFT,
        align_h   : AlignH               = AlignH.LEFT,
        align_v   : AlignV               = AlignV.TOP,
        width     : float                = -1.0,
        height    : float                = -1.0,
        color     : Color                = DEFAULT,
        family    : FontFamily           = DEFAULT,
        size      : FontSize             = DEFAULT,
        bold      : FontBool             = DEFAULT,
        italic    : FontBool             = DEFAULT,
        underline : FontBool             = DEFAULT,
        fresh     : bool                 = True,
        parent    : QGraphicsItem | None = None
    ) -> None:
        super().__init__(
            pos       = pos,
            rotation  = rotation,
            mirror_h  = mirror_h,
            mirror_v  = mirror_v,
            autoflip  = autoflip,
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
        self._tether = PropertyTextTetherItem(self)
        self._name = name
        self.setCleat(cleat, parent)
        self.onTextChange()

    def onSceneChange(self : Self, _scene : "DrawingScene | None") -> None:
        self.onSettingsChange()

    def onParentChange(self : Self, parent : QGraphicsItem | None) -> None:
        if parent is not None:
            self.onTextChange()
            self.quillSettingsChange()

    def onPositionChange(
        self : Self,
        pos  : QPointF | None = None
    ) -> None:
        ItemTransformMixin.onPositionChange(self, pos)
        if hasattr(self, "_tether"):
            self._tether.onPositionChange(pos)

    def onSelectionChange(self : Self, selected : bool) -> None:
        if self._cleat is None or self._cleat == "":
            return
        cleat_valid = self._cleat is not None and self._cleat != ""
        self._tether.setVisible(selected and cleat_valid)
        self._tether.anchor().grip().setVisible(selected and cleat_valid)

    def onSettingsChange(self : Self) -> None:
        if hasattr(self, "_tether"):
            self._tether.onSettingsChange()

    def onTextChange(self : Self) -> None:
        text = val2str(self.value())
        if text == "":
            text = f"<{self._name}>"
        super().setText(text)

    def cleat(self : Self) -> HandleId | None:
        return self._cleat

    def setCleat(
        self   : Self,
        id     : HandleId | None,
        parent : "ItemHandlesMixin | None" = None
    ) -> bool:
        self._cleat = id
        if id is None:
            return False
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
        ItemTransformMixin.setOrigin(self,  id)
        if hasattr(self, "_tether"):  # guard against partial initialisation
            self._tether.setParentItem(self.getOriginHandle())
            self._tether.onPositionChange(self.pos())

    def text(self : Self) -> str:
        raise NotImplementedError("PropertyTextItemMixin.text() is not implemented")

    def setText(self : Self, text : str) -> None:
        raise NotImplementedError("PropertyTextItemMixin.setText() is not implemented")

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

    def name(self : Self) -> str | None:
        return self._name if hasattr(self, "_name") else None

    def setName(self : Self, name : str) -> None:
        self._name = name
        self.onTextChange()

    def value(self : Self) -> Any:
        if not self.name():  # name is None or ""
            return None
        if self.owner() is None:
            return f"<{self.name()}>"
        return self.owner().properties.value(self.name(), self.onTextChange)

    def setValue(self : Self, value : Any) -> None:
        if not self.name():  # name is None or ""
            return
        if value is NO_CHANGE:
            return
        self.owner().properties.setValue(self.name(), value)

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
