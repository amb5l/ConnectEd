from typing      import Self, Any

from PyQt6.QtGui  import QColor

from .....properties import PropertyDisplay, PropertyState, PropertyEdit, \
                            PropertiesMixin

from .......core import Text, TextLine

from .......core.types import NoChange, NO_CHANGE, AlignH, AlignV

from .. import CmdBase


class CmdPropertyBase(CmdBase):
    _object : PropertiesMixin
    _state  : PropertyState

    def __init__(
        self   : Self,
        object : PropertiesMixin,
    ):
        super().__init__()
        self._object = object


class CmdAddProperty(CmdPropertyBase):
    _state : PropertyState

    def __init__(
        self      : Self,
        object    : PropertiesMixin,
        name      : str,
        value     : str | Text      = "",
        display   : PropertyDisplay = PropertyDisplay.NONE,
        cleat     : str             = NO_CHANGE,
        x         : float           = NO_CHANGE,
        y         : float           = NO_CHANGE,
        origin    : str             = NO_CHANGE,
        align_h   : AlignH          = NO_CHANGE,
        align_v   : AlignV          = NO_CHANGE,
        width     : float           = NO_CHANGE,
        height    : float           = NO_CHANGE,
        color     : QColor          = NO_CHANGE,
        family    : str             = NO_CHANGE,
        size      : float           = NO_CHANGE,
        bold      : bool            = NO_CHANGE,
        italic    : bool            = NO_CHANGE,
        underline : bool            = NO_CHANGE
    ):
        super().__init__(object)
        if isinstance(value, str):
            value = TextLine(value)
        state_args = {
            k: v for k, v in locals().items() \
                if k in PropertyState.__dataclass_fields__.keys()
        }
        self._state = PropertyState(**state_args)

    def redo(self : Self) -> None:
        self._object.addProperty(*self._state.astuple())

    def undo(self : Self) -> None:
        self._object.delProperty(self._state.name)


class CmdEditProperty(CmdPropertyBase):
    _before : PropertyState
    _after  : PropertyEdit

    def __init__(
        self      : Self,
        object    : PropertiesMixin,
        name      : str | tuple[str, str],
        value     : Any             | NoChange = NO_CHANGE,
        display   : PropertyDisplay | NoChange = NO_CHANGE,
        cleat     : str             | NoChange = NO_CHANGE,
        x         : float           | NoChange = NO_CHANGE,
        y         : float           | NoChange = NO_CHANGE,
        origin    : str             | NoChange = NO_CHANGE,
        align_h   : AlignH          | NoChange = NO_CHANGE,
        align_v   : AlignV          | NoChange = NO_CHANGE,
        width     : float | None    | NoChange = NO_CHANGE,
        height    : float | None    | NoChange = NO_CHANGE,
        color     : QColor          | NoChange = NO_CHANGE,
        family    : str             | NoChange = NO_CHANGE,
        size      : float           | NoChange = NO_CHANGE,
        bold      : bool            | NoChange = NO_CHANGE,
        italic    : bool            | NoChange = NO_CHANGE,
        underline : bool            | NoChange = NO_CHANGE,
    ):
        super().__init__(object)
        old_name, new_name = name if isinstance(name, tuple) else name, NO_CHANGE
        self._before = PropertyState.fromProperty(object, old_name)
        change_args = {
            k: v for k, v in locals().items() \
                if k in PropertyEdit.__dataclass_fields__.keys() \
                    and k != "name"
        }
        change_args["name"] = (name, new_name)
        self._after = PropertyEdit(**change_args)

    def redo(self : Self) -> None:
        args = self._after.asdict()
        args["name"] = self._before.name
        self._object.editProperty(**args)

    def undo(self : Self) -> None:
        self._object.editProperty(*self._before.astuple())
