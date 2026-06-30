from __future__ import annotations

from typing          import Self, Any
from collections.abc import Sequence

from PyQt6.QtGui import QColor

from ......core.check import checked
from ......core.types import NoChange, NO_CHANGE, AlignH, AlignV, \
                             HandleId, RectHandleId, DataKind

from .....dialogs.properties.types import (
    PropertyChangeBase,
    PropertyChangeAdd, PropertyChangeModify, PropertyChangeDelete,
    PropertyChangeTextAdd, PropertyChangeTextModify, PropertyChangeTextDelete
)

from ..cmd import cmdExec

from ..cmd.edit.properties import (
    CmdAddProperty, CmdEditProperty, CmdDelProperty,
    CmdAddPropertyText, CmdEditPropertyText, CmdDelPropertyText
)

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....properties import PropertiesMixin
    from .. import DiagramScene


class DiagramSceneApiPropertiesMixin:
    @checked
    def addProperty(
        self     : Self,
        object   : PropertiesMixin,
        name     : str,
        kind     : DataKind,
        value    : Any,
        undoable : bool = False
    ) -> None:
        from .. import DiagramScene
        if not isinstance(self, DiagramScene): raise TypeError("Bad host")
        cmd = CmdAddProperty(object, name, kind, value)
        cmdExec(self, cmd, undoable)

    @checked
    def editProperty(
        self     : Self,
        object   : PropertiesMixin,
        name     : str | tuple[str, str],
        kind     : DataKind | NoChange = NO_CHANGE,
        value    : Any      | NoChange = NO_CHANGE,
        undoable : bool = False
    ) -> None:
        from .. import DiagramScene
        if not isinstance(self, DiagramScene): raise TypeError("Bad host")
        cmd = CmdEditProperty(object, name, kind, value)
        cmdExec(self, cmd, undoable)

    @checked
    def delProperty(
        self     : Self,
        object   : PropertiesMixin,
        name     : str,
        undoable : bool = False
    ) -> None:
        from .. import DiagramScene
        if not isinstance(self, DiagramScene): raise TypeError("Bad host")
        cmd = CmdDelProperty(object, name)
        cmdExec(self, cmd, undoable)

    @checked
    def addPropertyText(
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
        underline  : bool,
        undoable   : bool = False
    ) -> None:
        from .. import DiagramScene
        if not isinstance(self, DiagramScene): raise TypeError("Bad host")
        cmd = CmdAddPropertyText(
            object, name, visible, cleat, x, y,
            rotation, mirror_h, mirror_v, autoflip,
            origin, align_h, align_v, width, height,
            pad_left, pad_right, pad_top, pad_bottom,
            color, font, size, bold, italic, underline
        )
        cmdExec(self, cmd, undoable)

    @checked
    def editPropertyText(
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
        undoable   : bool                    = False
    ) -> None:
        from .. import DiagramScene
        if not isinstance(self, DiagramScene): raise TypeError("Bad host")
        cmd = CmdEditPropertyText(
            object     = object,
            name       = name,
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
        cmdExec(self, cmd, undoable)

    @checked
    def delPropertyText(
        self     : Self,
        object   : PropertiesMixin,
        name     : str,
        undoable : bool = False
    ) -> None:
        from .. import DiagramScene
        if not isinstance(self, DiagramScene): raise TypeError("Bad host")
        cmd = CmdDelPropertyText(object, name)
        cmdExec(self, cmd, undoable)

    @checked
    def editProperties(
        self     : Self,
        object   : PropertiesMixin,
        changes  : Sequence[PropertyChangeBase],
        undoable : bool = False
    ) -> None:
        from .. import DiagramScene
        if not isinstance(self, DiagramScene): raise TypeError("Bad host")
        if len(changes) == 0:
            return
        if undoable:
            self.undo_stack.beginMacro("editProperties")
        for change in changes:
            args = vars(change)
            if isinstance(change, PropertyChangeDelete):
                self.delProperty(object, **args, undoable=undoable)
            elif isinstance(change, PropertyChangeAdd):
                self.addProperty(object, **args, undoable=undoable)
            elif isinstance(change, PropertyChangeModify):
                self.editProperty(object, **args, undoable=undoable)
            elif isinstance(change, PropertyChangeTextDelete):
                self.delPropertyText(object, **args, undoable=undoable)
            elif isinstance(change, PropertyChangeTextAdd):
                self.addPropertyText(object, **args, undoable=undoable)
            elif isinstance(change, PropertyChangeTextModify):
                self.editPropertyText(object, **args, undoable=undoable)
        if undoable:
            self.undo_stack.endMacro()
