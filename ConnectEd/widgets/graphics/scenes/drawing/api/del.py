from ..cmd import cmdExec, CmdRemoveProperty

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....properties import PropertiesMixin
    from .. import DrawingScene


def delProperty(
        self     : "DrawingScene",
        object   : PropertiesMixin,
        name     : str,
        undoable : bool = False
    ) -> None:
        cmd = CmdRemoveProperty(object, name)
        cmdExec(self, cmd, undoable)
