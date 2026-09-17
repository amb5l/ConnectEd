from __future__ import annotations

from typing      import Self, Any
from dataclasses import dataclass

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsScene, QMenu
from PyQt6.QtGui     import QAction, QColor

from ....app import settings

from ....core.check import checked
from ....core.types import NoChange, AlignH, AlignV, \
                                HandleId, RectHandleId, DataKind
from ....core.utils import val2str

from ..properties import (
    Property, PropertiesMixin, PropertySpec,
    PropertyDisplayState, PropertyDisplayChange
)

from .text   import TextItem
from .handle import HandleItem
from .tether import TextTetherItem

from .mixin.names      import ItemNamesMixin
from .mixin.transform  import ItemTransformMixin
from .mixin.handle     import ItemHandlesMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.diagram  import DiagramView


class PropertyTextTetherItem(TextTetherItem):
    """
    Tether line from the origin of a PropertyTextItem to its parent cleat.
    """

    def anchor(self : Self) -> QGraphicsItem | None:
        if isinstance(self._text_item, QGraphicsItem):
            return self._text_item.parentItem()
        return None


class PropertyTextItem(TextItem):
    # class attributes
    _PROPERTIES = \
        {
            "Name" : PropertySpec["PropertyTextItem"](
                kind   = DataKind.STR,
                getter = lambda self: self.name(),
                setter = lambda self, value: self.setName(value)
            ),
            "Visible" : PropertySpec["PropertyTextItem"](
                kind   = DataKind.BOOL,
                worthy = lambda self: not self.isVisible(),
                getter = lambda self: self.isVisible(),
                setter = lambda self, value: self.setVisible(value)
            ),
            "Cleat" : PropertySpec["PropertyTextItem"](
                kind   = lambda self: self.cleatKind(),
                getter = lambda self: self.cleat(),
                setter = lambda self, value: self.setCleat(value)
            )
        } | \
        ItemTransformMixin._PROPERTIES_POS | \
        ItemTransformMixin._PROPERTIES_ROTATE | \
        ItemTransformMixin._PROPERTIES_MIRROR | \
        ItemTransformMixin._PROPERTIES_RECT_ORIGIN | \
        TextItem._PROPERTIES_ALIGN | \
        TextItem._PROPERTIES_SIZE | \
        TextItem._PROPERTIES_APPEARANCE

    # instance attributes
    _property : Property
    _cleat    : HandleId | None
    _tether   : PropertyTextTetherItem | None

    def settingsName(self : Self) -> str:  # pyright: ignore[reportIncompatibleMethodOverride]
        """Instance method in this case."""
        if isinstance(item := self.owner(), ItemNamesMixin):
            settings_name = f"{item.settingsName()}{self._name}"
            settings_items = settings().get("theme/items")
            if hasattr(settings_items, settings_name):
                return settings_name
        return "PropertyText"

    def resourcesName(self : Self) -> str:  # pyright: ignore[reportIncompatibleMethodOverride]
        """Instance method in this case."""
        return self.settingsName()

    @checked
    def __init__(
        self       : Self,
        property   : Property,
        visible    : bool            = True,
        cleat      : HandleId | None = None,  # None for scene owner
        pos        : QPointF  | None = None,
        rotation   : float           = 0.0,
        mirror_h   : bool            = False,
        mirror_v   : bool            = False,
        autoflip   : bool            = True,
        origin     : RectHandleId    = RectHandleId.TOP_LEFT,
        align_h    : AlignH          = AlignH.LEFT,
        align_v    : AlignV          = AlignV.TOP,
        width      : float           = -1.0,
        height     : float           = -1.0,
        pad_left   : float           = 0.0,
        pad_right  : float           = 0.0,
        pad_top    : float           = 0.0,
        pad_bottom : float           = 0.0,
        color      : QColor   | None = None,
        font       : str      | None = None,
        size       : float    | None = None,
        bold       : bool     | None = None,
        italic     : bool     | None = None,
        underline  : bool     | None = None,
        fresh      : bool            = True
    ) -> None:
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
            fresh      = fresh
        )
        self._property = property
        self.setVisible(visible)
        self.setCleat(cleat)
        self._tether = PropertyTextTetherItem(self)
        self.onTextChanged()

    def onPositionChanged(
        self : Self,
        pos  : QPointF | None = None
    ) -> None:
        ItemTransformMixin.onPositionChanged(self, pos)
        if hasattr(self, "_tether") and self._tether is not None:
            self._tether.onPositionChanged(pos)

    def onSelectionChanged(self : Self, selected : bool) -> None:
        if (tether := self._tether) is None:
            return
        cleat = self._cleat
        if cleat is None or cleat == "":
            return
        cleat_valid = cleat is not None and cleat != ""
        tether.setVisible(selected and cleat_valid)
        if isinstance(anchor := tether.anchor(), HandleItem):
            grip = anchor.grip()
            grip.setVisible(selected and cleat_valid)

    def onTextChanged(self : Self) -> None:
        if isinstance(name := self.name(), str):
            if name in self.properties:
                kind = self.properties[name].kind()
                if kind in (DataKind.STR, DataKind.TEXT):
                    super().setBlock(kind == DataKind.TEXT)
                text = val2str(self.value())
            else:
                text = f"<{self._name} - not found>"
        else:
            text = f"<{self._name}>"
        super().setText(text)

    def cleatKind(self : Self) -> DataKind:
        item = self.owner()
        if not isinstance(item, ItemHandlesMixin):
            raise ValueError(f"Item {item} is not a handles item")
        return item.handleIdKind()

    def cleat(self : Self) -> HandleId | None:
        return self._cleat

    @checked
    def setVisible(self : Self, visible : bool) -> None:
        super().setVisible(visible)
        self._property.notify()

    @checked
    def setCleat(self : Self, id : HandleId | None) -> None:
        owner = self._property.owner()
        if isinstance(owner, QGraphicsItem):
            if not isinstance(owner, ItemHandlesMixin):
                raise ValueError(f"Owner {owner} has no handles")
            handles = owner.handles()
            if not handles:
                raise ValueError(f"Owner {owner} has no handles")
            if id is None:
                id = next(iter(handles))
            self.setParentItem(handles[id])
        elif isinstance(owner, QGraphicsScene):
            if id is not None:
                raise ValueError("Cleat cannot be set for scene owner")
        else:
            raise ValueError(f"Owner {owner} is not an item or scene")
        self._cleat = id
        self._property.notify()

    @checked
    def setOrigin(self : Self, id : HandleId) -> None:
        """Override to update tether line."""
        super().setOrigin(id)
        if hasattr(self, "_tether") and self._tether is not None:
            self._tether.setParentItem(self.getOriginHandle())
            self._tether.onPositionChanged(self.pos())

    def text(self : Self) -> str:
        raise NotImplementedError("text() is not implemented")

    @checked
    def setText(self : Self, text : str) -> None:
        raise NotImplementedError("setText() is not implemented")

    def block(self : Self) -> bool:
        raise NotImplementedError("block() is not implemented")

    @checked
    def setBlock(self : Self, block : bool) -> None:
        raise NotImplementedError("setBlock() is not implemented")

    def owner(self : Self) -> PropertiesMixin | None:
        if isinstance(parent := self.parentItem(), HandleItem):
            parent = parent.parentItem()
        return parent if isinstance(parent, PropertiesMixin) else None

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
        self.properties["Name"].notify()

    def value(self : Self) -> Any:
        name = self.name()
        if name is None or name == "":
            return None
        if not isinstance((item := self.owner()), PropertiesMixin):
            raise RuntimeError("Bad item")
        return item.properties[name].value()

    @checked
    def setValue(self : Self, value : Any) -> None:
        name = self.name()
        if name is None or name == "":
            return None
        if isinstance(value, NoChange):
            return
        self.properties[name].setValue(value)

    def state(self : Self) -> PropertyDisplayState:
        origin = self.origin()
        if not isinstance(origin, RectHandleId):
            raise ValueError(f"Origin {origin} is not a rect handle ID")
        return PropertyDisplayState(
            visible    = self.isVisible(),
            cleat      = self.cleat(),
            x          = self.pos().x(),
            y          = self.pos().y(),
            rotation   = self.rotation(),
            mirror_h   = self.mirrorH(),
            mirror_v   = self.mirrorV(),
            autoflip   = self.autoflip(),
            origin     = origin,
            align_h    = self.alignH(),
            align_v    = self.alignV(),
            width      = self.width(),
            height     = self.height(),
            pad_left   = self.padLeft(),
            pad_right  = self.padRight(),
            pad_top    = self.padTop(),
            pad_bottom = self.padBottom(),
            color      = self.textColor(),
            font       = self.textFont(),
            size       = self.textSize(),
            bold       = self.textBold(),
            italic     = self.textItalic(),
            underline  = self.textUnderline()
        )

    @checked
    def apply(
        self    : Self,
        payload : PropertyDisplayState | PropertyDisplayChange
    ) -> None:
        if not isinstance(payload.visible, NoChange):
            self.setVisible(payload.visible)
        if not isinstance(payload.cleat, NoChange):
            self.setCleat(payload.cleat)
        if not isinstance(payload.x, NoChange):
            self.setX(payload.x)
        if not isinstance(payload.y, NoChange):
            self.setY(payload.y)
        if not isinstance(payload.rotation, NoChange):
            self.setRotation(payload.rotation)
        if not isinstance(payload.mirror_h, NoChange):
            self.setMirrorH(payload.mirror_h)
        if not isinstance(payload.mirror_v, NoChange):
            self.setMirrorV(payload.mirror_v)
        if not isinstance(payload.autoflip, NoChange):
            self.setAutoflip(payload.autoflip)
        if not isinstance(payload.origin, NoChange):
            self.setOrigin(payload.origin)
        if not isinstance(payload.align_h, NoChange):
            self.setAlignH(payload.align_h)
        if not isinstance(payload.align_v, NoChange):
            self.setAlignV(payload.align_v)
        if not isinstance(payload.width, NoChange):
            self.setWidth(payload.width)
        if not isinstance(payload.height, NoChange):
            self.setHeight(payload.height)
        if not isinstance(payload.pad_left, NoChange):
            self.setPadLeft(payload.pad_left)
        if not isinstance(payload.pad_right, NoChange):
            self.setPadRight(payload.pad_right)
        if not isinstance(payload.pad_top, NoChange):
            self.setPadTop(payload.pad_top)
        if not isinstance(payload.pad_bottom, NoChange):
            self.setPadBottom(payload.pad_bottom)
        if not isinstance(payload.color, NoChange):
            self.setTextColor(payload.color)
        if not isinstance(payload.font, NoChange):
            self.setTextFont(payload.font)
        if not isinstance(payload.size, NoChange):
            self.setTextSize(payload.size)
        if not isinstance(payload.bold, NoChange):
            self.setTextBold(payload.bold)
        if not isinstance(payload.italic, NoChange):
            self.setTextItalic(payload.italic)
        if not isinstance(payload.underline, NoChange):
            self.setTextUnderline(payload.underline)

    @checked
    def applyDialog(self : Self, dialog : PropertyTextItemDialog) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        self._applyDialogCommon(dialog)
        name  = dialog.getName()
        kind  = dialog.getKind()
        value = dialog.getValue()
        cleat = dialog.getCleat()
        item = self.owner()
        if not isinstance(item, PropertiesMixin):
            raise RuntimeError("Bad item")
        old_name = self.name()
        if old_name is None:
            raise RuntimeError("PropertyTextItem has no name")
        if isinstance(name, NoChange):
            name = old_name
        elif name != old_name:
            item.propertyRename(old_name, name)
        if not isinstance(kind, NoChange):
            item.properties[name].setKind(kind)
        if not isinstance(value, NoChange):
            item.properties[name].setValue(value)
        if not isinstance(cleat, NoChange):
            self.setCleat(cleat)

    def propertyTuple(self : Self) -> tuple:
        return (
            self.name(),
            self.isVisible(),
            self.cleat(),
            self.pos().x(),
            self.pos().y(),
            self.rotation(),
            self.mirrorH(),
            self.mirrorV(),
            self.autoflip(),
            self.origin(),
            self.alignH(),
            self.alignV(),
            self.width(),
            self.height(),
            self.padLeft(),
            self.padRight(),
            self.padTop(),
            self.padBottom(),
            self.color(),
            self.textFont(),
            self.textSize(),
            self.textBold(),
            self.textItalic(),
            self.textUnderline()
        )

    @checked
    def ctxMenuItems(
        self : Self,
        view : DiagramView,
        spos : QPointF
    ) -> list[QAction | QMenu]:
        items : list[QAction | QMenu] = [
            view.action("Edit...", lambda: view.editPropertyTextDialog(self)),
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
            view.action("Appearance...", lambda: view.editAppearance(self)),
            view.action("Properties...", lambda: view.editItemProperties(self))
        ]
        return items


@dataclass
class PropertyTextSpec:
    visible    : bool            = True
    cleat      : HandleId | None = None
    x          : float           = 0
    y          : float           = 0
    rotation   : float           = 0.0
    mirror_h   : bool            = False
    mirror_v   : bool            = False
    autoflip   : bool            = True
    origin     : RectHandleId    = RectHandleId.TOP_LEFT
    align_h    : AlignH          = AlignH.LEFT
    align_v    : AlignV          = AlignV.TOP
    width      : float           = -1.0
    height     : float           = -1.0
    pad_left   : float           = 0.0
    pad_right  : float           = 0.0
    pad_top    : float           = 0.0
    pad_bottom : float           = 0.0
    color      : QColor   | None = None
    font       : str      | None = None
    size       : float    | None = None
    bold       : bool     | None = None
    italic     : bool     | None = None
    underline  : bool     | None = None

    def astuple(self : Self) -> tuple:
        return (
            self.visible, self.cleat, self.x, self.y,
            self.rotation, self.mirror_h, self.mirror_v, self.autoflip,
            self.origin, self.align_h, self.align_v, self.width, self.height,
            self.pad_left, self.pad_right, self.pad_top, self.pad_bottom,
            self.color, self.font, self.size, self.bold, self.italic, self.underline
        )
