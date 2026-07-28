from __future__ import annotations

from typing import Self

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QGraphicsItem

from ......core.check import checked

from ....items.polyline  import PolylineItem, PolyVtxItem
from ....items.block     import BlockItem
from ....items.block_pin import BlockPinItem

from ..cmd import cmdExec, CmdAdd

from ..cmd.polyline  import CmdAddPolyVtx
from ..cmd.block_pin import CmdAddBlockPin

class DiagramSceneApiAddMixin:

    @checked
    def addItems(
        self     : Self,
        items    : QGraphicsItem | list[QGraphicsItem],
        undoable : bool = False
    ) -> None:
        """Add an item to the scene."""
        from .. import DiagramScene
        if not isinstance(self, DiagramScene): raise TypeError("Bad host")
        cmd = CmdAdd(self, items)
        cmdExec(self, cmd, undoable)

    @checked
    def addPolyVtx(
        self     : Self,
        polyline : PolylineItem,
        pos      : QPointF,
        sweep    : float | None = None,
        undoable : bool = False
    ) -> PolyVtxItem:
        """Add a vertex to a polyline."""
        from .. import DiagramScene
        if not isinstance(self, DiagramScene): raise TypeError("Bad host")
        cmd = CmdAddPolyVtx(polyline, pos, sweep)
        cmdExec(self, cmd, undoable)
        if (vtx := cmd.vtx()) is None:
            raise RuntimeError("Failed to add vertex")
        return vtx

    @checked
    def addBlockPin(
        self     : Self,
        parent   : BlockItem,
        pin      : BlockPinItem,
        undoable : bool = False
    ) -> BlockPinItem:
        """Add a block pin to the scene."""
        from .. import DiagramScene
        if not isinstance(self, DiagramScene): raise TypeError("Bad host")
        cmd = CmdAddBlockPin(parent, pin)
        cmdExec(self, cmd, undoable)
        return cmd.pin()
