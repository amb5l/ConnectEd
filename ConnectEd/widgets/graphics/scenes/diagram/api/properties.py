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
    PropertyTextChangeAdd, PropertyTextChangeModify, PropertyTextChangeDelete
)

from ....properties import PropertyDisplayChange

from ..cmd import cmdExec

from ..cmd.edit.properties import (
    CmdAddProperty, CmdEditProperty, CmdDelProperty,
    CmdSetPropertyDisplay, CmdEditPropertyDisplay
)

from ..host import asDiagramScene

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....properties import PropertiesMixin


class DiagramSceneApiPropertiesMixin:
    @checked
    def addProperty(
        self     : Self,
        owner    : PropertiesMixin,
        name     : str,
        kind     : DataKind,
        value    : Any,
        undoable : bool = False
    ) -> None:
        host = asDiagramScene(self)
        cmd = CmdAddProperty(owner, name, kind, value)
        cmdExec(host, cmd, undoable)

    @checked
    def editProperty(
        self     : Self,
        owner    : PropertiesMixin,
        name     : str | tuple[str, str],
        kind     : DataKind | NoChange = NO_CHANGE,
        value    : Any      | NoChange = NO_CHANGE,
        undoable : bool = False
    ) -> None:
        host = asDiagramScene(self)
        cmd = CmdEditProperty(owner, name, kind, value)
        cmdExec(host, cmd, undoable)

    @checked
    def delProperty(
        self     : Self,
        owner    : PropertiesMixin,
        name     : str,
        undoable : bool = False
    ) -> None:
        host = asDiagramScene(self)
        cmd = CmdDelProperty(owner, name)
        cmdExec(host, cmd, undoable)

    @checked
    def setPropertyDisplay(
        self       : Self,
        owner      : PropertiesMixin,
        name       : str,
        enable     : bool,
        undoable   : bool = False
    ) -> None:
        host = asDiagramScene(self)
        cmd = CmdSetPropertyDisplay(owner, name, enable)

    @checked
    def editPropertyDisplay(
        self       : Self,
        owner      : PropertiesMixin,
        name       : str,
        visible    : bool            | NoChange = NO_CHANGE,
        cleat      : HandleId | None | NoChange = NO_CHANGE,
        x          : float           | NoChange = NO_CHANGE,
        y          : float           | NoChange = NO_CHANGE,
        rotation   : float           | NoChange = NO_CHANGE,
        mirror_h   : bool            | NoChange = NO_CHANGE,
        mirror_v   : bool            | NoChange = NO_CHANGE,
        autoflip   : bool            | NoChange = NO_CHANGE,
        origin     : RectHandleId    | NoChange = NO_CHANGE,
        align_h    : AlignH          | NoChange = NO_CHANGE,
        align_v    : AlignV          | NoChange = NO_CHANGE,
        width      : float           | NoChange = NO_CHANGE,
        height     : float           | NoChange = NO_CHANGE,
        pad_left   : float           | NoChange = NO_CHANGE,
        pad_right  : float           | NoChange = NO_CHANGE,
        pad_top    : float           | NoChange = NO_CHANGE,
        pad_bottom : float           | NoChange = NO_CHANGE,
        color      : QColor   | None | NoChange = NO_CHANGE,
        font       : str      | None | NoChange = NO_CHANGE,
        size       : float    | None | NoChange = NO_CHANGE,
        bold       : bool     | None | NoChange = NO_CHANGE,
        italic     : bool     | None | NoChange = NO_CHANGE,
        underline  : bool     | None | NoChange = NO_CHANGE,
        undoable   : bool = False
    ) -> None:
        host = asDiagramScene(self)
        cmd = CmdEditPropertyDisplay(owner, name, PropertyDisplayChange(
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
        ))
        cmdExec(host, cmd, undoable)

    @checked
    def editProperties(
        self     : Self,
        object   : PropertiesMixin,
        changes  : Sequence[PropertyChangeBase],
        undoable : bool = False
    ) -> None:
        host = asDiagramScene(self)
        if len(changes) == 0:
            return
        if undoable:
            host.undo_stack.beginMacro("editProperties")
        for change in changes:
            args = vars(change)
            if isinstance(change, PropertyChangeDelete):
                host.delProperty(object, **args, undoable=undoable)
            elif isinstance(change, PropertyChangeAdd):
                host.addProperty(object, **args, undoable=undoable)
            elif isinstance(change, PropertyChangeModify):
                host.editProperty(object, **args, undoable=undoable)
            elif isinstance(change, PropertyTextChangeDelete):
                host.delPropertyText(object, **args, undoable=undoable)
            elif isinstance(change, PropertyTextChangeAdd):
                host.addPropertyText(object, **args, undoable=undoable)
            elif isinstance(change, PropertyTextChangeModify):
                host.editPropertyText(object, **args, undoable=undoable)
        if undoable:
            host.undo_stack.endMacro()
