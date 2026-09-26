from __future__ import annotations

from typing      import Self, Any
from dataclasses import dataclass, fields

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsScene, QMenu
from PyQt6.QtGui     import QAction, QColor

from ....app           import settings

from ....core.check    import checked
from ....core.types    import NoChange, NO_CHANGE, AlignH, AlignV, \
                           HandleId, RectHandleId, DataKind
from ....core.utils    import val2str

from ...graphics.quill import Quill

from ..properties      import Property, PropertiesMixin, PropertySpec

from .text             import TextItem
from .handle           import HandleItem
from .tether           import TextTetherItem

from .mixin.names      import ItemNamesMixin
from .mixin.transform  import ItemTransformMixin
from .mixin.handle     import ItemHandlesMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.diagram  import DiagramView
    from ..scenes.diagram import DiagramScene


class PropertyTextTetherItem(TextTetherItem):
    """
    Tether line from the origin of a PropertyTextItem to its parent cleat.
    """

    def anchor(self : Self) -> QGraphicsItem | None:
        if isinstance(self._text_item, QGraphicsItem):
            return self._text_item.parentItem()
        return None


class PropertyTextItem(TextItem):
    """A tethered text item for displaying a property value."""

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
        TextItem._PROPERTIES_AUTOFLIP | \
        TextItem._PROPERTIES_ALIGN | \
        TextItem._PROPERTIES_SIZE | \
        TextItem._PROPERTIES_PADDING | \
        TextItem._PROPERTIES_TYPOGRAPHY

    # instance attributes
    _property : Property
    _cleat    : HandleId               | None
    _tether   : PropertyTextTetherItem | None

    def settingsName(self : Self) -> str:  # pyright: ignore[reportIncompatibleMethodOverride]
        """Instance method in this case."""
        if isinstance(owner := self.owner(), ItemNamesMixin) \
        and hasattr(self, "_property"):
            return type(self)._themeItemName(owner, self.name())
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
        self._updateQuill()
        self._property.subscribe(self.onTextChanged)

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
        kind = self._property.kind()
        if kind in (DataKind.STR, DataKind.TEXT):
            super().setBlock(kind == DataKind.TEXT)
        text = val2str(self._property.value())
        if text == "":
            text = f"<{self.name()}>"
        super().setText(text)

    def property(self : Self) -> Property:
        return self._property

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

    def name(self : Self) -> str:
        return self._property.name()

    @checked
    def setName(self : Self, name : str) -> None:
        old = self.name()
        if old == name:
            return
        if not self._property.owner().propertyRename(old, name):
            return
        self.properties["Name"].notify()
        self._updateQuill()

    def value(self : Self) -> Any:
        return self._property.value()

    @checked
    def setValue(self : Self, value : Any) -> None:
        if isinstance(value, NoChange):
            return
        self._property.setValue(value)

    def state(self : Self) -> PropertyTextState:
        origin = self.origin()
        if not isinstance(origin, RectHandleId):
            raise ValueError(f"Origin {origin} is not a rect handle ID")
        return PropertyTextState(
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
        payload : PropertyTextSpec | PropertyTextState | PropertyTextChange
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

    @classmethod
    def _themeItemName(
        cls       : type[Self],
        owner     : ItemNamesMixin | type[ItemNamesMixin],
        prop_name : str
    ) -> str:
        settings_name = f"{owner.settingsName()}{prop_name}"
        items = settings().get("theme/items")
        if hasattr(items, settings_name):
            return settings_name
        return "PropertyText"


@dataclass
class PropertyTextSpec:
    """Used to specify property texts during owner construction."""

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


@dataclass
class PropertyTextState:
    """Used to capture property text states in editor dialogs."""

    visible    : bool
    cleat      : HandleId | None
    x          : float
    y          : float
    rotation   : float
    mirror_h   : bool
    mirror_v   : bool
    autoflip   : bool
    origin     : RectHandleId
    align_h    : AlignH
    align_v    : AlignV
    width      : float
    height     : float
    pad_left   : float
    pad_right  : float
    pad_top    : float
    pad_bottom : float
    color      : QColor   | None
    font       : str      | None
    size       : float    | None
    bold       : bool     | None
    italic     : bool     | None
    underline  : bool     | None


@dataclass
class PropertyTextPending:
    """Working copy of a property text inside an editor dialog."""

    obj   : PropertyTextItem  | None  # None if new
    state : PropertyTextState | None  # None if deleted

    @checked
    def __init__(
        self   : Self,
        source : PropertyTextItem | PropertyTextState
    ) -> None:
        if isinstance(source, PropertyTextItem):
            self.obj   = source
            self.state = source.state()
        else:
            self.obj   = None
            self.state = source

    @checked
    def getEdit(
        self     : Self,
        owner    : PropertiesMixin,
        property : Property
    ) -> PropertyTextAdd | PropertyTextDelete | PropertyTextChange | None:
        """Return the property text edit this pending produces, or None."""
        if self.state is None:
            if self.obj is None:
                return None
            return PropertyTextDelete(self.obj)
        if self.obj is None:
            return PropertyTextAdd(owner, property, self.state)
        change = PropertyTextChange.fromComparison(self)
        if change.noop():
            return None
        return change


@dataclass
class PropertyTextEdit:
    """Base class for property text edits."""

    pass


@dataclass
class PropertyTextAdd(PropertyTextEdit):
    """Property Text Edit: add a new property text."""

    owner    : PropertiesMixin
    property : Property
    state    : PropertyTextState


@dataclass
class PropertyTextDelete(PropertyTextEdit):
    """Property Text Edit: delete an existing property text."""

    item : PropertyTextItem


@dataclass
class PropertyTextChange(PropertyTextEdit):
    """Property Text Edit: change an existing property text."""

    item       : PropertyTextItem
    visible    : bool            | NoChange = NO_CHANGE
    cleat      : HandleId | None | NoChange = NO_CHANGE
    x          : float           | NoChange = NO_CHANGE
    y          : float           | NoChange = NO_CHANGE
    rotation   : float           | NoChange = NO_CHANGE
    mirror_h   : bool            | NoChange = NO_CHANGE
    mirror_v   : bool            | NoChange = NO_CHANGE
    autoflip   : bool            | NoChange = NO_CHANGE
    origin     : RectHandleId    | NoChange = NO_CHANGE
    align_h    : AlignH          | NoChange = NO_CHANGE
    align_v    : AlignV          | NoChange = NO_CHANGE
    width      : float           | NoChange = NO_CHANGE
    height     : float           | NoChange = NO_CHANGE
    pad_left   : float           | NoChange = NO_CHANGE
    pad_right  : float           | NoChange = NO_CHANGE
    pad_top    : float           | NoChange = NO_CHANGE
    pad_bottom : float           | NoChange = NO_CHANGE
    color      : QColor   | None | NoChange = NO_CHANGE
    font       : str      | None | NoChange = NO_CHANGE
    size       : float    | None | NoChange = NO_CHANGE
    bold       : bool     | None | NoChange = NO_CHANGE
    italic     : bool     | None | NoChange = NO_CHANGE
    underline  : bool     | None | NoChange = NO_CHANGE

    @classmethod
    def fromComparison(
        cls     : type[Self],
        pending : PropertyTextPending
    ) -> Self:
        if pending.obj is None or pending.state is None:
            raise ValueError("Property text pending has no item or state")
        before = pending.obj.state()
        after  = pending.state
        kwargs : dict[str, Any] = {}
        for field in fields(before):
            before_value = getattr(before, field.name)
            after_value  = getattr(after,  field.name)
            if before_value != after_value:
                kwargs[field.name] = after_value
        return cls(pending.obj, **kwargs)

    def noop(self : Self) -> bool:
        """Return True if the edit is a no-op."""
        return all(
            isinstance(getattr(self, field.name), NoChange)
            for field in fields(PropertyTextState)
        )
