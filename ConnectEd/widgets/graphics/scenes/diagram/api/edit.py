from ......core.types import EdgeLoc

from ....items.block     import BlockItem
from ....items.block_pin import BlockPinItem

from ...drawing.api import DrawingSceneApiEditMixin

from ...drawing.cmd import cmdExec

from ..cmd.block_pin import CmdMoveBlockPins

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DiagramScene


class DiagramSceneApiEditMixin(DrawingSceneApiEditMixin):
    def editMoveBlockPins(
        self     : "DiagramScene",
        parent   : BlockItem,
        pins     : list[BlockPinItem],
        after    : dict[BlockPinItem, EdgeLoc],
        before   : dict[BlockPinItem, EdgeLoc],
        undoable : bool = False
    ) -> None:
        cmd = CmdMoveBlockPins(parent, pins, after, before)
        cmdExec(self, cmd, undoable)
