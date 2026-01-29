from typing      import Self, Any
from dataclasses import astuple

from PyQt6.QtGui  import QColor

from .....properties import PropertyDisplay, \
                            PropertyState, PropertyChange, \
                            PropertiesMixin

from .......core import Text, TextLine

from .....items import NoChange, NO_CHANGE, AlignH, AlignV

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
        width     : float | None    = NO_CHANGE,
        height    : float | None    = NO_CHANGE,
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
        self._object.addProperty(*astuple(self._state))

    def undo(self : Self) -> None:
        self._object.delProperty(self._state.name)


class CmdEditProperty(CmdPropertyBase):
    _before : PropertyState
    _after  : PropertyChange

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
        if isinstance(name, tuple):
            name, new_name = name
        else:
            new_name = NO_CHANGE
        self._before = PropertyState.fromProperty(object, name)
        name = new_name
        change_args = {
            k: v for k, v in locals().items() \
                if k in PropertyChange.__dataclass_fields__.keys()
        }
        self._after = PropertyChange(**change_args)

    def redo(self : Self) -> None:
        self._object.editProperty(astuple(self._after))

    def undo(self : Self) -> None:
        self._object.editProperty(astuple(self._before))



        if self._after.value is not NO_CHANGE:
            self._object.setPropertyValue(name, self._after.value)
        if self._after.display is PropertyDisplay.NONE:
            if self._before.text is not None:
                # remove
                self._object.delPropertyText(name)
        else:
            if self._before.text is None:
                # add
                self._object.addPropertyText(
                    name      = name,
                    visible   = self._after.display == PropertyDisplay.SHOW,
                    cleat     = self._after.cleat,
                    pos_x     = self._after.x,
                    pos_y     = self._after.y,
                    origin    = self._after.origin,
                    align_h   = self._after.align_h,
                    align_v   = self._after.align_v,
                    width     = self._after.width,
                    height    = self._after.height,
                    color     = self._after.color,
                    family    = self._after.family,
                    size      = self._after.size,
                    bold      = self._after.bold,
                    italic    = self._after.italic,
                    underline = self._after.underline
                )
            else:
                # modify
                self._object.editPropertyText(
                    name      = name,
                    visible   = self._after.display == PropertyDisplay.SHOW,
                    cleat     = self._after.cleat,
                    pos_x     = self._after.x,
                    pos_y     = self._after.y,
                    origin    = self._after.origin,
                    align_h   = self._after.align_h,
                    align_v   = self._after.align_v,
                    width     = self._after.width,
                    height    = self._after.height,
                    color     = self._after.color,
                    family    = self._after.family,
                    size      = self._after.size,
                    bold      = self._after.bold,
                    italic    = self._after.italic,
                    underline = self._after.underline
                )

    def undo(self : Self) -> None:
        # undo name change
        name = self._after.name
        if self._after.name is not NO_CHANGE:
            self._object.renProperty(self._after.name, self._before.name)
            name = self._before.name
        # undo value change
        if self._after.value is not NO_CHANGE:
            self._object.setPropertyValue(name, self._before.value)
        # undo property text change
        if self._before.text is None:
            # undo add
            self._object.delPropertyText(name)
        else:
            # undo remove or modify
            if self._after.text is None:
                # undo remove
                self._object.setPropertyText(self._before.text)
            else:
                # undo modify
                text : PropertyTextState = self._before.text
                self._object.editPropertyText(
                    name      = name,
                    visible   = text.visible,
                    cleat     = text.cleat,
                    pos_x     = text.pos_x,
                    pos_y     = text.pos_y,
                    origin    = text.origin,
                    align_h   = text.align_h,
                    align_v   = text.align_v,
                    width     = text.width,
                    height    = text.height,
                    color     = text.color,
                    family    = text.family,
                    size      = text.size,
                    bold      = text.bold,
                    italic    = text.italic,
                    underline = text.underline
                )
