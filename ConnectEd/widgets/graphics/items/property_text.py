from typing import Self, Any

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QGraphicsItem, QMenu
from PyQt6.QtGui     import QAction, QColor

from ....app import settings, logger

from ....core.check import checked
from ....core.types import NO_CHANGE, AlignH, AlignV, \
                           HandleId, RectHandleId, DataKind
from ....core.utils import val2str

from ..properties import InherentProperty, PropertiesMixin

from . import ItemType

from .text   import TextItem
from .handle import HandleItem
from .tether import TextTetherItem


from .mixin.transform import ItemTransformMixin
from .mixin.handle    import ItemHandlesMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.drawing  import DrawingView
    from ...dialogs.items.property_text import PropertyTextItemDialog


class PropertyTextTetherItem(TextTetherItem):
    """
    Tether line from the origin of a PropertyTextItem to its parent cleat.
    """

    _text_item : "PropertyTextItem"

    def anchor(self : Self) -> "HandleItem | None":
        return self._text_item.parentItem()


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
        TextItem._PROPERTIES_TEXT

    # instance attributes
    _name   : str
    _cleat  : HandleId | None
    _tether : PropertyTextTetherItem | None

    def settingsName(self : Self) -> str:
        item = self.item()
        if item is not None and hasattr(self, "_name"):
            settings_name = f"{item.settingsName()}{self._name}"
            settings_items = settings().get("theme/items")
            if hasattr(settings_items, settings_name):
                return settings_name
        return "PropertyText"

    @checked
    def __init__(
        self       : Self,
        name       : str                  = "",
        cleat      : HandleId      | None = None,
        pos        : QPointF       | None = None,
        rotation   : float                = 0.0,
        mirror_h   : bool                 = False,
        mirror_v   : bool                 = False,
        autoflip   : bool                 = True,
        origin     : RectHandleId         = RectHandleId.TOP_LEFT,
        align_h    : AlignH               = AlignH.LEFT,
        align_v    : AlignV               = AlignV.TOP,
        width      : float                = -1.0,
        height     : float                = -1.0,
        pad_left   : float                = 0.0,
        pad_right  : float                = 0.0,
        pad_top    : float                = 0.0,
        pad_bottom : float                = 0.0,
        color      : QColor        | None = None,
        font       : str           | None = None,
        size       : float         | None = None,
        bold       : bool          | None = None,
        italic     : bool          | None = None,
        underline  : bool          | None = None,
        fresh      : bool                 = True,
        parent     : QGraphicsItem | None = None
    ) -> None:
        self._name = name
        super().__init__(
            pos        = pos,
            rotation   = rotation,
            mirror_h   = mirror_h,
            mirror_v   = mirror_v,
            autoflip   = autoflip,
            origin     = origin,
            align_h    = align_h,
            align_v    = align_v,
            width      = width,
            height     = height,
            pad_left   = pad_left,
            pad_right  = pad_right,
            pad_top    = pad_top,
            pad_bottom = pad_bottom,
            color      = color,
            font       = font,
            size       = size,
            bold       = bold,
            italic     = italic,
            underline  = underline,
            fresh      = fresh,
            parent     = parent
        )
        self._tether = PropertyTextTetherItem(self)
        self.setCleat(cleat, parent)
        self.onTextChanged()

    def onParentChanged(self : Self, parent : QGraphicsItem | None) -> None:
        if parent is not None:
            self.onTextChanged()

    def onPositionChanged(
        self : Self,
        pos  : QPointF | None = None
    ) -> None:
        ItemTransformMixin.onPositionChanged(self, pos)
        if hasattr(self, "_tether"):
            self._tether.onPositionChanged(pos)

    def onSelectionChanged(self : Self, selected : bool) -> None:
        if self._cleat is None or self._cleat == "":
            return
        cleat_valid = self._cleat is not None and self._cleat != ""
        self._tether.setVisible(selected and cleat_valid)
        self._tether.anchor().grip().setVisible(selected and cleat_valid)

    def onTextChanged(self : Self) -> None:
        owner = self.owner()
        if owner is not None and self.name():
            kind = owner.properties.kind(self.name())
            if kind in (DataKind.STR, DataKind.TEXT):
                super().setBlock(kind == DataKind.TEXT)
        text = val2str(self.value())
        if text == "":
            text = f"<{self._name}>"
        super().setText(text)

    def cleat(self : Self) -> HandleId | None:
        return self._cleat

    @checked
    def setVisible(self : Self, visible : bool) -> None:
        super().setVisible(visible)
        self.properties.signalChanges("Visible")

    @checked
    def setCleat(
        self   : Self,
        id     : HandleId | None,
        parent : "ItemHandlesMixin | None" = None
    ) -> bool:
        self._cleat = id
        ok = False
        if id is not None:
            item = parent or self.item()
            if item is not None:
                for child in item.childItems():
                    if isinstance(child, HandleItem) and child.id() == id:
                        self.setParentItem(child)
                        ok = True
                        break
                if not ok:
                    logger().warning("Cleat not found in parent item")
        self.properties.signalChanges("Cleat")
        return ok

    @checked
    def setOrigin(self : Self, id : RectHandleId) -> None:
        """Override to update tether line."""
        ItemTransformMixin.setOrigin(self,  id)
        if hasattr(self, "_tether"):  # guard against partial initialisation
            self._tether.setParentItem(self.getOriginHandle())
            self._tether.onPositionChanged(self.pos())

    def text(self : Self) -> str:
        raise NotImplementedError("text() is not implemented")

    def setText(self : Self, text : str) -> None:
        raise NotImplementedError("setText() is not implemented")

    def block(self : Self) -> bool:
        raise NotImplementedError("block() is not implemented")

    @checked
    def setBlock(self : Self, _block : bool) -> None:
        raise NotImplementedError("setBlock() is not implemented")

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

    @checked
    def bind(self : Self, name : str) -> None:
        """Rebind to an owner property (does not signal this item's Name)."""
        self._name = name
        self.onTextChanged()
        self._updateQuill()

    def name(self : Self) -> str | None:
        return self._name if hasattr(self, "_name") else None

    @checked
    def setName(self : Self, name : str) -> None:
        self.bind(name)
        self.properties.signalChanges("Name")

    def value(self : Self) -> Any:
        if not self.name():  # name is None or ""
            return None
        if self.owner() is None:
            return f"<{self.name()}>"
        return self.owner().properties.value(self.name(), self.onTextChanged)

    @checked
    def setValue(self : Self, value : Any) -> None:
        if not self.name():  # name is None or ""
            return
        if value is NO_CHANGE:
            return
        self.owner().properties.setValue(self.name(), value)

    @checked
    def applyDialog(self : Self, dialog : "PropertyTextItemDialog") -> None:
        self._applyDialogCommon(dialog)
        name     = dialog.getName()
        kind     = dialog.getKind()
        value    = dialog.getValue()
        cleat    = dialog.getCleat()
        owner    = self.owner()
        old_name = self.name()
        if name is not NO_CHANGE and name != old_name:
            if owner is not None and old_name:
                owner.properties.rename(old_name, name)
            else:
                self.setName(name)
        name = self.name()
        if owner is not None and name:
            if kind is not NO_CHANGE:
                owner.properties.setKind(name, kind)
            if value is not NO_CHANGE:
                owner.properties.setValue(name, value)
        if cleat is not NO_CHANGE:
            self.setCleat(cleat)

    @checked
    def ctxMenuItems(self : Self, view : "DrawingView", _spos : QPointF) -> list[QAction | QMenu]:
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
