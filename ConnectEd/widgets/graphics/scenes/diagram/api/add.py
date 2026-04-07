from ....items.block     import BlockItem
from ....items.block_pin import BlockPinItem

from ...drawing.api import DrawingSceneApiAddMixin

from ...drawing.cmd import cmdExec

from ..cmd.block_pin import CmdAddBlockPin


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DiagramScene


class DiagramSceneApiAddMixin(DrawingSceneApiAddMixin):
    def addBlockPin(
        self     : "DiagramScene",
        parent   : BlockItem,
        pin      : BlockPinItem,
        undoable : bool = False
    ) -> BlockPinItem:
        """Add a block pin to the scene."""
        cmd = CmdAddBlockPin(parent, pin)
        cmdExec(self, cmd, undoable)
        return cmd.pin()
