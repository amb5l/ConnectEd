from typing      import Self, Any
from dataclasses import dataclass

from PyQt6.QtGui  import QColor

from .......app import logger

from .......core.check import checked
from .......core.types import NoChange, NO_CHANGE, AlignH, AlignV, DataKind, \
                              HandleId, RectHandleId

from .....properties import PropertiesMixin

from .....items.property_text import PropertyTextItem

from .. import CmdBase


class CmdPropertyBase(CmdBase):
    _object : PropertiesMixin
    _name   : str

    @checked
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

    @checked
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

    @checked
    def redo(self : Self) -> None:
        self._object.properties.add(self._name, self._kind, self._value)

    @checked
    def undo(self : Self) -> None:
        self._object.properties.delete(self._name)


class CmdEditProperty(CmdBase):
    @dataclass
    class State:
        name  : str      | NoChange
        kind  : DataKind | NoChange
        value : Any      | NoChange

    _object    : PropertiesMixin
    _old_name  : str
    _old_kind  : DataKind
    _old_value : Any
    _new_name  : str      | NoChange
    _new_kind  : DataKind | NoChange
    _new_value : Any      | NoChange

    @checked
    def __init__(
        self   : Self,
        object : PropertiesMixin,
        name   : str | tuple[str, str],
        kind   : DataKind | NoChange = NO_CHANGE,
        value  : Any      | NoChange = NO_CHANGE
    ) -> None:
        super().__init__()
        self._object = object
        # unpack name/rename
        old_name, new_name = \
            name if isinstance(name, tuple) else (name, NO_CHANGE)
        # detect unknown property
        if not object.properties.has(old_name):
            logger().warning(f"Property '{old_name}' not found")
            self.setObsolete(True)
            return
        # build old state
        old_kind = object.properties.kind(old_name)
        if old_kind is None:
            logger().error(f"Property '{old_name}' has no kind")
            self.setObsolete(True)
            return
        old_value = object.properties.value(old_name)
        self._old_name  = old_name
        self._old_kind  = old_kind
        self._old_value = old_value
        self._new_name  = NO_CHANGE if old_name == new_name else new_name
        self._new_kind  = NO_CHANGE if old_kind == kind else kind
        self._new_value = NO_CHANGE if old_value == value else value

    @checked
    def redo(self : Self) -> None:
        name = self._old_name
        if not isinstance(self._new_name, NoChange):
            self._object.properties.rename(name, self._new_name)
            name = self._new_name
        if not isinstance(self._new_kind, NoChange):
            self._object.properties.setKind(name, self._new_kind)
        if not isinstance(self._new_value, NoChange):
            self._object.properties.setValue(name, self._new_value)

    @checked
    def undo(self : Self) -> None:
        if not isinstance(self._new_name, NoChange):
            self._object.properties.rename(self._new_name, self._old_name)
        name = self._old_name
        if not isinstance(self._old_kind, NoChange):
            self._object.properties.setKind(name, self._old_kind)
        if not isinstance(self._old_value, NoChange):
            self._object.properties.setValue(name, self._old_value)


class CmdDelProperty(CmdPropertyBase):
    _kind  : DataKind
    _value : Any
    _pt    : PropertyTextItem | None

    @checked
    def __init__(
        self : Self,
        obj  : PropertiesMixin,
        name : str
    ) -> None:
        super().__init__(obj, name)
        kind = obj.properties.kind(name)
        if kind is None:
            logger().error(f"Property '{name}' has no kind")
            self.setObsolete(True)
            return
        self._kind  = kind
        self._value = obj.properties.value(name)
        self._pt    = obj.properties.text(name)

    @checked
    def redo(self : Self) -> None:
        self._object.properties.delete(self._name)

    @checked
    def undo(self : Self) -> None:
        self._object.properties.add(self._name, self._kind, self._value)
        if self._pt:
            self._object.properties.setText(self._name, self._pt)


class CmdPropertyTextItemBase(CmdPropertyBase):
    @dataclass
    class PropertyTextItemState:
        visible    : bool
        cleat      : HandleId
        x          : float
        y          : float
        rotation   : float
        mirror_h   : bool
        mirror_v   : bool
        autoflip   : bool
        origin     : RectHandleId | None
        align_h    : AlignH
        align_v    : AlignV
        width      : float
        height     : float
        pad_left   : float
        pad_right  : float
        pad_top    : float
        pad_bottom : float
        color      : QColor | None
        font       : str    | None
        size       : float  | None
        bold       : bool   | None
        italic     : bool   | None
        underline  : bool   | None

    @dataclass
    class PropertyTextItemChange:
        visible    : bool                | NoChange = NO_CHANGE
        cleat      : HandleId            | NoChange = NO_CHANGE
        x          : float               | NoChange = NO_CHANGE
        y          : float               | NoChange = NO_CHANGE
        rotation   : float               | NoChange = NO_CHANGE
        mirror_h   : bool                | NoChange = NO_CHANGE
        mirror_v   : bool                | NoChange = NO_CHANGE
        autoflip   : bool                | NoChange = NO_CHANGE
        origin     : RectHandleId | None | NoChange = NO_CHANGE
        align_h    : AlignH              | NoChange = NO_CHANGE
        align_v    : AlignV              | NoChange = NO_CHANGE
        width      : float               | NoChange = NO_CHANGE
        height     : float               | NoChange = NO_CHANGE
        pad_left   : float               | NoChange = NO_CHANGE
        pad_right  : float               | NoChange = NO_CHANGE
        pad_top    : float               | NoChange = NO_CHANGE
        pad_bottom : float               | NoChange = NO_CHANGE
        color      : QColor       | None | NoChange = NO_CHANGE
        font       : str          | None | NoChange = NO_CHANGE
        size       : float        | None | NoChange = NO_CHANGE
        bold       : bool         | None | NoChange = NO_CHANGE
        italic     : bool         | None | NoChange = NO_CHANGE
        underline  : bool         | None | NoChange = NO_CHANGE


class CmdAddPropertyText(CmdPropertyTextItemBase):
    _state : CmdPropertyTextItemBase.PropertyTextItemState

    @checked
    def __init__(
        self       : Self,
        object     : PropertiesMixin,
        name       : str,
        visible    : bool,
        cleat      : HandleId,
        x          : float,
        y          : float,
        rotation   : float,
        mirror_h   : bool,
        mirror_v   : bool,
        autoflip   : bool,
        origin     : RectHandleId,
        align_h    : AlignH,
        align_v    : AlignV,
        width      : float,
        height     : float,
        pad_left   : float,
        pad_right  : float,
        pad_top    : float,
        pad_bottom : float,
        color      : QColor,
        font       : str,
        size       : float,
        bold       : bool,
        italic     : bool,
        underline  : bool
    ) -> None:
        super().__init__(object, name)
        self._state = self.PropertyTextItemState(
            visible    = visible,
            cleat      = cleat,
            x          = x,
            y          = y,
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
            font      = font,
            size      = size,
            bold      = bold,
            italic    = italic,
            underline = underline,
        )

    @checked
    def redo(self : Self) -> None:
        self._object.properties.addText(self._name, **vars(self._state))

    @checked
    def undo(self : Self) -> None:
        self._object.properties.delText(self._name)


class CmdEditPropertyText(CmdPropertyTextItemBase):
    _before : CmdPropertyTextItemBase.PropertyTextItemState  | None
    _after  : CmdPropertyTextItemBase.PropertyTextItemChange | None

    @checked
    def __init__(
        self       : Self,
        object     : PropertiesMixin,
        name       : str,
        visible    : bool         | NoChange = NO_CHANGE,
        cleat      : HandleId     | NoChange = NO_CHANGE,
        x          : float        | NoChange = NO_CHANGE,
        y          : float        | NoChange = NO_CHANGE,
        rotation   : float        | NoChange = NO_CHANGE,
        mirror_h   : bool         | NoChange = NO_CHANGE,
        mirror_v   : bool         | NoChange = NO_CHANGE,
        autoflip   : bool         | NoChange = NO_CHANGE,
        origin     : RectHandleId | NoChange = NO_CHANGE,
        align_h    : AlignH       | NoChange = NO_CHANGE,
        align_v    : AlignV       | NoChange = NO_CHANGE,
        width      : float        | NoChange = NO_CHANGE,
        height     : float        | NoChange = NO_CHANGE,
        pad_left   : float        | NoChange = NO_CHANGE,
        pad_right  : float        | NoChange = NO_CHANGE,
        pad_top    : float        | NoChange = NO_CHANGE,
        pad_bottom : float        | NoChange = NO_CHANGE,
        color      : QColor       | NoChange = NO_CHANGE,
        font       : str          | NoChange = NO_CHANGE,
        size       : float        | NoChange = NO_CHANGE,
        bold       : bool         | NoChange = NO_CHANGE,
        italic     : bool         | NoChange = NO_CHANGE,
        underline  : bool         | NoChange = NO_CHANGE,
    ) -> None:
        super().__init__(object, name)
        pt = object.properties.text(name)
        if pt is None:
            self._before = None
            self._after = None
            logger().error(f"Property '{name}' does not have a text item")
            self.setObsolete(True)
            return
        old_cleat = pt.cleat()
        if not isinstance(old_cleat, HandleId):
            logger().error(f"Property text '{name}' has no cleat")
            self.setObsolete(True)
            return
        old_origin = pt.origin()
        if not isinstance(old_origin, RectHandleId):
            logger().error(f"Property text '{name}' has no origin")
            self.setObsolete(True)
            return
        self._before = self.PropertyTextItemState(
            visible    = pt.isVisible(),
            cleat      = old_cleat,
            x          = pt.x(),
            y          = pt.y(),
            rotation   = pt.rotation(),
            mirror_h   = pt.mirrorH(),
            mirror_v   = pt.mirrorV(),
            autoflip   = pt.autoflip(),
            origin     = old_origin,
            align_h    = pt.alignH(),
            align_v    = pt.alignV(),
            width      = pt.width(),
            height     = pt.height(),
            pad_left   = pt.padLeft(),
            pad_right  = pt.padRight(),
            pad_top    = pt.padTop(),
            pad_bottom = pt.padBottom(),
            color      = pt.textColor(),
            font       = pt.textFont(),
            size       = pt.textSize(),
            bold       = pt.textBold(),
            italic     = pt.textItalic(),
            underline  = pt.textUnderline()
        )
        self._after = self.PropertyTextItemChange(
            visible    = visible,
            cleat      = cleat,
            x          = x,
            y          = y,
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
            underline  = underline
        )
        # mark obsolete if new state is unchanged
        changed = False
        for field in self._after.__dataclass_fields__.keys():
            new_value = getattr(self._after, field)
            if new_value is not NO_CHANGE:
                if new_value != getattr(self._before, field):
                    changed = True
                    break
        self.setObsolete(not changed)

    @checked
    def redo(self : Self) -> None:
        if self._after is None:
            return
        self._object.properties.editText(self._name, **vars(self._after))

    @checked
    def undo(self : Self) -> None:
        if self._before is None:
            return
        self._object.properties.editText(self._name, **vars(self._before))

class CmdDelPropertyText(CmdPropertyTextItemBase):
    _pt     : PropertyTextItem | None
    _before : CmdPropertyTextItemBase.PropertyTextItemState  | None
    _after  : CmdPropertyTextItemBase.PropertyTextItemChange | None

    @checked
    def __init__(
        self   : Self,
        object : PropertiesMixin,
        name   : str
    ) -> None:
        super().__init__(object, name)
        self._pt = object.properties.text(name)
        if self._pt is None:
            logger().warning(f"Property '{name}' does not have a text item")

    @checked
    def redo(self : Self) -> None:
        self._object.properties.delText(self._name)

    @checked
    def undo(self : Self) -> None:
        self._object.properties.addText(self._name, **vars(self._before))
