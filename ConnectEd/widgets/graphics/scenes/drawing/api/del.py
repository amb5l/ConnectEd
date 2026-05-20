from ......core.check import checked

from ..cmd import cmdExec
from ..cmd.edit.properties import CmdDelProperty

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....properties import PropertiesMixin
    from .. import DrawingScene


@checked
def delProperty(
    self     : "DrawingScene",
    object   : PropertiesMixin,
    name     : str,
    undoable : bool = False
) -> None:
    cmd = CmdDelProperty(object, name)
    cmdExec(self, cmd, undoable)
