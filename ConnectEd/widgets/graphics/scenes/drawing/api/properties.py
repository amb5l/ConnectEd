from typing import Any

from PyQt6.QtGui import QColor

from ......core.types import NoChange, NO_CHANGE, AlignH, AlignV, \
                             HandleId, RectHandleId, DataKind

from ..cmd import cmdExec

from ..cmd.edit.properties import (
    CmdAddProperty, CmdEditProperty, CmdDelProperty,
    CmdAddPropertyText, CmdEditPropertyText, CmdDelPropertyText
)

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....properties import PropertiesMixin
    from .. import DrawingScene

class DrawingSceneApiPropertiesMixin:
    def addProperty(
        self     : "DrawingScene",
        object   : "PropertiesMixin",
        name     : str,
        kind     : DataKind,
        value    : Any,
        undoable : bool = False
    ) -> None:
        cmd = CmdAddProperty(object, name, kind, value)
        cmdExec(self, cmd, undoable)

    def editProperty(
        self     : "DrawingScene",
        object   : "PropertiesMixin",
        name     : str | tuple[str, str] | NoChange = NO_CHANGE,
        kind     : DataKind              | NoChange = NO_CHANGE,
        value    : Any                   | NoChange = NO_CHANGE,
        undoable : bool = False
    ) -> None:
        cmd = CmdEditProperty(object, name, kind, value)
        cmdExec(self, cmd, undoable)

    def delProperty(
        self     : "DrawingScene",
        object   : "PropertiesMixin",
        name     : str,
        undoable : bool = False
    ) -> None:
        cmd = CmdDelProperty(object, name)
        cmdExec(self, cmd, undoable)

    def addPropertyText(
        self     : "DrawingScene",
        object   : "PropertiesMixin",
        name     : str,
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
        underline : bool,
        undoable  : bool = False
    ) -> None:
        cmd = CmdAddPropertyText(
            object, name, visible, cleat, x, y, rotation, flip,
            origin, align_h, align_v, width, height,
            color, family, size, bold, italic, underline
        )
        cmdExec(self, cmd, undoable)

    def editPropertyText(
        self      : "DrawingScene",
        object    : "PropertiesMixin",
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
        underline : bool,
        undoable  : bool = False
    ) -> None:
        cmd = CmdEditPropertyText(
            object, name, visible, cleat, x, y, rotation, flip,
            origin, align_h, align_v, width, height,
            color, family, size, bold, italic, underline
        )
        cmdExec(self, cmd, undoable)

    def delPropertyText(
        self     : "DrawingScene",
        object   : "PropertiesMixin",
        name     : str,
        undoable : bool = False
    ) -> None:
        cmd = CmdDelPropertyText(object, name)
        cmdExec(self, cmd, undoable)
