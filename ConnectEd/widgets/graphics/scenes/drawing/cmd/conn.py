from typing      import Self
from dataclasses import dataclass

from PyQt6.QtCore import QPointF

from ......app import logger

from ....items.conn_vtx import ConnVtx
from ....items.conn_seg import ConnSeg
from ....items.entry    import Entry

from . import CmdSceneBase

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingScene


class CmdAddConnVtx(CmdSceneBase):
    """Create and add a new vertex to the scene."""

    # instance attributes
    _vtx : ConnVtx

    def __init__(
        self  : Self,
        scene : "DrawingScene",
        pos   : QPointF,
        cls   : type[ConnVtx] = ConnVtx
    ) -> None:
        super().__init__(scene)
        self._vtx = cls(pos)

    def redo(self : Self) -> None:
        self._scene.addItem(self._vtx)

    def undo(self : Self) -> None:
        self._scene.removeItem(self._vtx)

    def vtx(self : Self) -> ConnVtx:
        return self._vtx


class CmdReparentConnVtx(CmdSceneBase):
    @dataclass
    class ConnVtxState:
        parent : Entry   | None
        pos    : QPointF | None

    # instance attributes
    _vtx    : ConnVtx
    _before : ConnVtxState
    _after  : ConnVtxState

    def __init__(
        self   : Self,
        scene  : "DrawingScene",
        vtx    : ConnVtx,
        parent : Entry | None
    ) -> None:
        super().__init__(scene)
        self._vtx = vtx
        self._before = self.ConnVtxState(vtx.parentItem(), vtx.pos())
        self._after = self.ConnVtxState(
            parent,
            QPointF() if parent is not None else
            self._before.pos if self._before.parent is None else
            self._before.parent.scenePos()
        )

    def redo(self : Self) -> None:
        self._vtx.setParentItem(self._after.parent)
        self._vtx.setPos(self._after.pos)

    def undo(self : Self) -> None:
        self._vtx.setParentItem(self._before.parent)
        self._vtx.setPos(self._before.pos)


class CmdRemoveConnVtx(CmdSceneBase):
    """Remove a specified vertex from the scene."""

    # instance attributes
    _vtx : ConnVtx

    def __init__(
        self  : Self,
        scene : "DrawingScene",
        vtx   : ConnVtx
    ) -> None:
        super().__init__(scene)
        self._vtx = vtx

    def redo(self : Self) -> None:
        self._scene.removeItem(self._vtx)

    def undo(self : Self) -> None:
        self._scene.addItem(self._vtx)


class CmdAddConnSeg(CmdSceneBase):
    """Add a new segment to the scene between two specified vertices."""

    # instance attributes
    _vtx1 : ConnVtx
    _vtx2 : ConnVtx
    _seg  : ConnSeg

    def __init__(
        self : Self,
        scene : "DrawingScene",
        vtx1 : ConnVtx,
        vtx2 : ConnVtx,
        cls  : type[ConnSeg] = ConnSeg
    ) -> None:
        super().__init__(scene)
        self._vtx1 = vtx1
        self._vtx2 = vtx2
        self._seg = cls()

    def redo(self : Self) -> None:
        # attach segment to vertices
        self._seg.setVtx1(self._vtx1)
        self._seg.setVtx2(self._vtx2)
        # add segment to scene
        self._scene.addItem(self._seg)

    def undo(self : Self) -> None:
        # detach segment from vertices
        self._seg.setVtx1(None)
        self._seg.setVtx2(None)
        # remove segment from scene
        self._scene.removeItem(self._seg)

    def seg(self : Self) -> ConnSeg:
        return self._seg


class CmdReattachConnSeg(CmdSceneBase):
    """Detach a segment from one vertex and attach it to another."""

    # instance attributes
    _seg     : ConnSeg
    _vtx_old : ConnVtx
    _vtx_new : ConnVtx

    def __init__(
        self    : Self,
        scene   : "DrawingScene",
        seg     : ConnSeg,
        vtx_old : ConnVtx,
        vtx_new : ConnVtx
    ) -> None:
        super().__init__(scene)
        self._seg = seg
        self._vtx_old = vtx_old
        self._vtx_new = vtx_new

    def redo(self : Self) -> None:
        if not self._seg.reattach(self._vtx_old, self._vtx_new):
            logger().warning(f"Failed to reattach segment {self._seg} to {self._vtx_new}")

    def undo(self : Self) -> None:
        if not self._seg.reattach(self._vtx_new, self._vtx_old):
            logger().warning(f"Failed to reattach segment {self._seg} to {self._vtx_old}")


class CmdRemoveConnSeg(CmdSceneBase):
    """Remove a specified segment from the scene."""

    # instance attributes
    _vtx1 : ConnVtx
    _vtx2 : ConnVtx
    _seg  : ConnSeg

    def __init__(
        self : Self,
        scene : "DrawingScene",
        seg : ConnSeg
    ) -> None:
        super().__init__(scene)
        self._vtx1 = seg.vtx1()
        self._vtx2 = seg.vtx2()
        self._seg = seg

    def redo(self : Self) -> None:
        self._seg.setVtx1(None)
        self._seg.setVtx2(None)
        self._scene.removeItem(self._seg)

    def undo(self : Self) -> None:
        self._seg.setVtx1(self._vtx1)
        self._seg.setVtx2(self._vtx2)
        self._scene.addItem(self._seg)
