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

from ..host import asDiagramScene


class DiagramSceneApiAddMixin:
    @checked
    def addItems(
        self     : Self,
        items    : QGraphicsItem | list[QGraphicsItem],
        undoable : bool = False
    ) -> None:
        """Add an item to the scene."""
        host = asDiagramScene(self)
        cmd = CmdAdd(host, items)
        cmdExec(host, cmd, undoable)

    @checked
    def addPolyVtx(
        self     : Self,
        polyline : PolylineItem,
        pos      : QPointF,
        sweep    : float | None = None,
        undoable : bool = False
    ) -> PolyVtxItem:
        """Add a vertex to a polyline."""
        host = asDiagramScene(self)
        cmd = CmdAddPolyVtx(polyline, pos, sweep)
        cmdExec(host, cmd, undoable)
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
        host = asDiagramScene(self)
        cmd = CmdAddBlockPin(parent, pin)
        cmdExec(host, cmd, undoable)
        return cmd.pin()
