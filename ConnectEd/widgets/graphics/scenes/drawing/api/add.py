from PyQt6.QtCore import QPointF

from ....items import ItemType

from ....items.block     import Block
from ....items.block_pin import BlockPin
from ....items.polyline  import Polyline, PolyVtx

from ..cmd           import cmdExec, CmdAdd
from ..cmd.block_pin import CmdAddBlockPin
from ..cmd.polyline  import CmdAddPolyVtx


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingScene


class DrawingSceneApiAddMixin:
    """Methods to add items to the scene."""

    def addItems(
        self     : "DrawingScene",
        items    : list[ItemType],
        undoable : bool = False
    ) -> None:
        """Add an item to the scene."""
        cmd = CmdAdd(self, items, self.selectedItems() if undoable else [])
        cmdExec(self, cmd, undoable)

    def addBlockPin(
        self     : "DrawingScene",
        parent   : Block,
        pin      : BlockPin,
        undoable : bool = False
    ) -> BlockPin:
        """Add a block pin to the scene."""
        cmd = CmdAddBlockPin(parent, pin)
        cmdExec(self, cmd, undoable)
        return cmd.pin()

    def addPolyline(
        self     : "DrawingScene",
        vertices : list[QPointF],
        closed   : bool = False,
        undoable : bool = False
    ) -> Polyline:
        """Add a polyline to the scene."""
        item = Polyline(vertices, closed)
        self.addItems([item], undoable)
        return item

    def addPolyVtx(
        self     : "DrawingScene",
        polyline : Polyline,
        pos      : QPointF,
        undoable : bool = False
    ) -> PolyVtx:
        """Add a vertex to a polyline."""
        cmd = CmdAddPolyVtx(polyline, pos)
        cmdExec(self, cmd, undoable)
        return cmd.vtx()
