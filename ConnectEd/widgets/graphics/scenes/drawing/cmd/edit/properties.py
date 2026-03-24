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
    ):
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
    ):
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
    ):
        super().__init__(object, name)
        self._kind  = object.getPropertyKind(name)
        self._value = object.getPropertyValue(name)
        self._pt    = object.getPropertyTextItem(name)

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
        flip      : bool
        origin    : RectHandleId
        align_h   : AlignH
        align_v   : AlignV
        width     : float
        height    : float
        color     : QColor
        family    : str
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
        flip      : bool,
        origin    : RectHandleId,
        align_h   : AlignH,
        align_v   : AlignV,
        width     : float,
        height    : float,
        color     : QColor,
        family    : str,
        size      : float,
        bold      : bool,
        italic    : bool,
        underline : bool
    ):
        super().__init__(object, name)
        self._state = self.PropertyTextItemState(
            visible   = visible,
            cleat     = cleat,
            x         = x,
            y         = y,
            rotation  = rotation,
            flip      = flip,
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
        rotation  : float        | NoChange = NO_CHANGE,
        flip      : bool         | NoChange = NO_CHANGE,
        x         : float        | NoChange = NO_CHANGE,
        y         : float        | NoChange = NO_CHANGE,
        origin    : RectHandleId | NoChange = NO_CHANGE,
        align_h   : AlignH       | NoChange = NO_CHANGE,
        align_v   : AlignV       | NoChange = NO_CHANGE,
        width     : float        | NoChange = NO_CHANGE,
        height    : float        | NoChange = NO_CHANGE,
        color     : QColor       | NoChange = NO_CHANGE,
        family    : str          | NoChange = NO_CHANGE,
        size      : float        | NoChange = NO_CHANGE,
        bold      : bool         | NoChange = NO_CHANGE,
        italic    : bool         | NoChange = NO_CHANGE,
        underline : bool         | NoChange = NO_CHANGE,
    ):
        super().__init__(object, name)
        pt = object.getPropertyTextItem(name)
        if pt is None:
            self._old = None
            self._new = None
            logger().warning(f"Property '{name}' does not have a text item")
            return
        self._old.visible   = pt.isVisible()
        self._old.cleat     = pt.cleat()
        self._old.x         = pt.x()
        self._old.y         = pt.y()
        self._old.rotation  = pt.rotation()
        self._old.flip      = pt.flip()
        self._old.origin    = pt.origin()
        self._old.align_h   = pt.alignH()
        self._old.align_v   = pt.alignV()
        self._old.width     = pt.width()
        self._old.height    = pt.height()
        self._old.color     = pt.quillColor()
        self._old.family    = pt.quillFamily()
        self._old.size      = pt.quillSize()
        self._old.bold      = pt.quillBold()
        self._old.italic    = pt.quillItalic()
        self._old.underline = pt.quillUnderline()
        self._new.visible   = visible
        self._new.cleat     = cleat
        self._new.x         = x
        self._new.y         = y
        self._new.rotation  = rotation
        self._new.flip      = flip
        self._new.origin    = origin
        self._new.align_h   = align_h
        self._new.align_v   = align_v
        self._new.width     = width
        self._new.height    = height
        self._new.color     = color
        self._new.family    = family
        self._new.size      = size
        self._new.bold      = bold
        self._new.italic    = italic
        self._new.underline = underline

    def redo(self : Self) -> None:
        if self._new is None:
            return
        self._object.editPropertyTextItem(
            self._name,
            self._new.visible,
            self._new.cleat,
            self._new.x,
            self._new.y,
            self._new.rotation,
            self._new.flip,
            self._new.origin,
            self._new.align_h,
            self._new.align_v,
            self._new.width,
            self._new.height,
            self._new.color,
            self._new.family,
            self._new.size,
            self._new.bold,
            self._new.italic,
            self._new.underline
        )

    def undo(self : Self) -> None:
        if self._old is None:
            return
        self._object.editPropertyTextItem(
            self._name,
            self._old.visible,
            self._old.cleat,
            self._old.x,
            self._old.y,
            self._old.rotation,
            self._old.flip,
            self._old.origin,
            self._old.align_h,
            self._old.align_v,
            self._old.width,
            self._old.height,
            self._old.color,
            self._old.family,
            self._old.size,
            self._old.bold,
            self._old.italic,
            self._old.underline
        )

class CmdDelPropertyText(CmdPropertyTextItemBase):
    _pt : PropertyTextItem | None

    def __init__(
        self   : Self,
        object : PropertiesMixin,
        name   : str
    ):
        super().__init__(object, name)
        self._pt = object.getPropertyTextItem(name)
        if self._pt is None:
            logger().warning(f"Property '{name}' does not have a text item")

    def redo(self : Self) -> None:
        self._object.delPropertyTextItem(self._name)

    def undo(self : Self) -> None:
        self._object.setPropertyTextItem(self._name, self._pt)
