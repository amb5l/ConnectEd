from typing      import Self, Any
from dataclasses import dataclass

from PyQt6.QtGui  import QColor

from .......app import logger

from .......core.types import NoChange, NO_CHANGE, AlignH, AlignV, DataKind, \
                              HandleId, RectHandleId

from .....properties import PropertiesMixin

from .....items.property_text import PropertyTextItem

from .. import CmdBase


class CmdPropertyBase(CmdBase):
    _object : PropertiesMixin
    _name   : str

    def __init__(
        self   : Self,
        object : PropertiesMixin,
        name   : str
    ) -> None:
        super().__init__()
        self._object = object
        self._name = name


class CmdAddProperty(CmdPropertyBase):
    _name  : str
    _kind  : DataKind
    _value : Any

    def __init__(
        self   : Self,
        object : PropertiesMixin,
        name   : str,
        kind   : DataKind,
        value  : Any
    ) -> None:
        super().__init__(object, name)
        self._kind  = kind
        self._value = value

    def redo(self : Self) -> None:
        self._object.properties.add(self._name, self._kind, self._value)

    def undo(self : Self) -> None:
        self._object.properties.delete(self._name)


class CmdEditProperty(CmdBase):
    @dataclass
    class State:
        name  : str
        kind  : DataKind
        value : Any

    _object : PropertiesMixin
    _old    : State
    _new    : State

    def __init__(
        self   : Self,
        object : PropertiesMixin,
        name   : str | tuple[str, str] | NoChange = NO_CHANGE,
        kind   : DataKind              | NoChange = NO_CHANGE,
        value  : Any                   | NoChange = NO_CHANGE
    ) -> None:
        super().__init__()
        self._object = object
        # unpack name/rename
        name, rename = name if isinstance(name, tuple) else (name, NO_CHANGE)
        # detect unknown property
        if not object.properties.has(name):
            logger().warning(f"Property '{name}' not found")
            self.setObsolete(True)
            return
        # build old state
        self._old = self.State(
            name, object.properties.kind(name), object.properties.value(name)
        )
        # detect no changes
        if name == rename:
            rename = NO_CHANGE
        if kind == self._old.kind:
            kind = NO_CHANGE
        if value == self._old.value:
            value = NO_CHANGE
        if rename is NO_CHANGE and kind is NO_CHANGE and value is NO_CHANGE:
            self.setObsolete(True)
            return
        # build new state
        self._new = self.State(rename, kind, value)
        # done
        return

    def redo(self : Self) -> None:
        name = self._old.name
        if self._new.name is not NO_CHANGE:
            self._object.properties.rename(name, name := self._new.name)
        if self._new.kind is not NO_CHANGE:
            self._object.properties.setKind(name, self._new.kind)
        if self._new.value is not NO_CHANGE:
            self._object.properties.setValue(name, self._new.value)

    def undo(self : Self) -> None:
        if self._new.name is not NO_CHANGE:
            self._object.properties.rename(self._new.name, self._old.name)
        name = self._old.name
        if self._new.kind is not NO_CHANGE:
            self._object.properties.setKind(name, self._old.kind)
        if self._new.value is not NO_CHANGE:
            self._object.properties.setValue(name, self._old.value)


class CmdDelProperty(CmdPropertyBase):
    _kind  : DataKind
    _value : Any
    _pt    : PropertyTextItem

    def __init__(
        self   : Self,
        object : PropertiesMixin,
        name   : str
    ) -> None:
        super().__init__(object, name)
        self._kind  = object.properties.kind(name)
        self._value = object.properties.value(name)
        self._pt    = object.properties.text(name)

    def redo(self : Self) -> None:
        self._object.properties.delete(self._name)

    def undo(self : Self) -> None:
        self._object.properties.add(self._name, self._kind, self._value)
        if self._pt:
            self._object.properties.setText(self._name, self._pt)


class CmdPropertyTextItemBase(CmdPropertyBase):
    @dataclass
    class PropertyTextItemState:
        visible   : bool
        cleat     : HandleId
        x         : float
        y         : float
        rotation  : float
        mirror_h  : bool
        mirror_v  : bool
        autoflip  : bool
        origin    : RectHandleId
        align_h   : AlignH
        align_v   : AlignV
        width     : float
        height    : float
        color     : QColor
        font      : str
        size      : float
        bold      : bool
        italic    : bool
        underline : bool


class CmdAddPropertyText(CmdPropertyTextItemBase):
    _state : CmdPropertyTextItemBase.PropertyTextItemState

    def __init__(
        self      : Self,
        object    : PropertiesMixin,
        name      : str,
        visible   : bool,
        cleat     : HandleId,
        x         : float,
        y         : float,
        rotation  : float,
        mirror_h  : bool,
        mirror_v  : bool,
        autoflip  : bool,
        origin    : RectHandleId,
        align_h   : AlignH,
        align_v   : AlignV,
        width     : float,
        height    : float,
        color     : QColor,
        font      : str,
        size      : float,
        bold      : bool,
        italic    : bool,
        underline : bool
    ) -> None:
        super().__init__(object, name)
        self._state = self.PropertyTextItemState(
            visible   = visible,
            cleat     = cleat,
            x         = x,
            y         = y,
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
            font      = font,
            size      = size,
            bold      = bold,
            italic    = italic,
            underline = underline,
        )

    def redo(self : Self) -> None:
        self._object.properties.addText(self._name, **vars(self._state))

    def undo(self : Self) -> None:
        self._object.properties.delText(self._name)


class CmdEditPropertyText(CmdPropertyTextItemBase):
    _old : CmdPropertyTextItemBase.PropertyTextItemState | None
    _new : CmdPropertyTextItemBase.PropertyTextItemState | None

    def __init__(
        self      : Self,
        object    : PropertiesMixin,
        name      : str,
        visible   : bool         | NoChange = NO_CHANGE,
        cleat     : HandleId     | NoChange = NO_CHANGE,
        x         : float        | NoChange = NO_CHANGE,
        y         : float        | NoChange = NO_CHANGE,
        rotation  : float        | NoChange = NO_CHANGE,
        mirror_h  : bool         | NoChange = NO_CHANGE,
        mirror_v  : bool         | NoChange = NO_CHANGE,
        autoflip  : bool         | NoChange = NO_CHANGE,
        origin    : RectHandleId | NoChange = NO_CHANGE,
        align_h   : AlignH       | NoChange = NO_CHANGE,
        align_v   : AlignV       | NoChange = NO_CHANGE,
        width     : float        | NoChange = NO_CHANGE,
        height    : float        | NoChange = NO_CHANGE,
        color     : QColor       | NoChange = NO_CHANGE,
        font      : str          | NoChange = NO_CHANGE,
        size      : float        | NoChange = NO_CHANGE,
        bold      : bool         | NoChange = NO_CHANGE,
        italic    : bool         | NoChange = NO_CHANGE,
        underline : bool         | NoChange = NO_CHANGE,
    ) -> None:
        super().__init__(object, name)
        pt = object.properties.text(name)
        if pt is None:
            self._old = None
            self._new = None
            logger().warning(f"Property '{name}' does not have a text item")
            return
        self._old = self.PropertyTextItemState(
            visible   = pt.isVisible(),
            cleat     = pt.cleat(),
            x         = pt.x(),
            y         = pt.y(),
            rotation  = pt.rotation(),
            mirror_h  = pt.mirrorH(),
            mirror_v  = pt.mirrorV(),
            autoflip  = pt.autoflip(),
            origin    = pt.origin(),
            align_h   = pt.alignH(),
            align_v   = pt.alignV(),
            width     = pt.width(),
            height    = pt.height(),
            color     = pt.textColor(),
            font      = pt.textFont(),
            size      = pt.textSize(),
            bold      = pt.textBold(),
            italic    = pt.textItalic(),
            underline = pt.textUnderline(),
        )
        self._new = self.PropertyTextItemState(
            visible   = visible,
            cleat     = cleat,
            x         = x,
            y         = y,
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
            font      = font,
            size      = size,
            bold      = bold,
            italic    = italic,
            underline = underline,
        )
        # mark obsolete if new state is unchanged
        changed = False
        for field in self._new.__dataclass_fields__.keys():
            new_value = getattr(self._new, field)
            if new_value is not NO_CHANGE:
                if new_value != getattr(self._old, field):
                    changed = True
                    break
        self.setObsolete(not changed)

    def redo(self : Self) -> None:
        if self._new is None:
            return
        self._object.properties.editText(self._name, **vars(self._new))

    def undo(self : Self) -> None:
        if self._old is None:
            return
        self._object.properties.editText(self._name, **vars(self._old))

class CmdDelPropertyText(CmdPropertyTextItemBase):
    _pt : PropertyTextItem | None

    def __init__(
        self   : Self,
        object : PropertiesMixin,
        name   : str
    ) -> None:
        super().__init__(object, name)
        self._pt = object.properties.text(name)
        if self._pt is None:
            logger().warning(f"Property '{name}' does not have a text item")

    def redo(self : Self) -> None:
        self._object.delPropertyTextItem(self._name)

    def undo(self : Self) -> None:
        self._object.setPropertyTextItem(self._name, self._pt)
