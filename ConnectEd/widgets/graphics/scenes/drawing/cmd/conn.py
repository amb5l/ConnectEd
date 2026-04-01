from typing      import Self

from PyQt6.QtCore import QPointF

from ......app import logger

from ....items.vertex  import VertexItem
from ....items.segment import SegmentItem

from . import CmdSceneBase

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingScene


class CmdAddVertex(CmdSceneBase):
    """Create and add a new vertex to the scene."""

    # instance attributes
    _vtx : VertexItem

    def __init__(
        self  : Self,
        scene : "DrawingScene",
        pos   : QPointF
    ) -> None:
        super().__init__(scene)
        self._vtx = VertexItem(pos, scene._id_vtx.next())

    def redo(self : Self) -> None:
        self._scene.addItem(self._vtx)

    def undo(self : Self) -> None:
        self._scene.removeItem(self._vtx)

    def vtx(self : Self) -> VertexItem:
        return self._vtx


class CmdRemoveVertex(CmdSceneBase):
    """Remove a specified vertex from the scene."""

    # instance attributes
    _vtx : VertexItem

    def __init__(
        self  : Self,
        scene : "DrawingScene",
        vtx   : VertexItem
    ) -> None:
        super().__init__(scene)
        self._vtx = vtx

    def redo(self : Self) -> None:
        self._scene.removeItem(self._vtx)

    def undo(self : Self) -> None:
        self._scene.addItem(self._vtx)


class CmdAddSegment(CmdSceneBase):
    """Add a new segment to the scene between two specified vertices."""

    # instance attributes
    _vtx1 : VertexItem
    _vtx2 : VertexItem
    _seg  : SegmentItem

    def __init__(
        self  : Self,
        scene : "DrawingScene",
        vtx1  : VertexItem,
        vtx2  : VertexItem
    ) -> None:
        super().__init__(scene)
        self._vtx1 = vtx1
        self._vtx2 = vtx2
        self._seg = SegmentItem()

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

    def seg(self : Self) -> SegmentItem:
        return self._seg


class CmdReattachSegment(CmdSceneBase):
    """
    Detach a segment from one vertex and attach it to another.
    """

    # instance attributes
    _seg     : SegmentItem
    _vtx_old : VertexItem
    _vtx_new : VertexItem

    def __init__(
        self    : Self,
        scene   : "DrawingScene",
        seg     : SegmentItem,
        vtx_old : VertexItem,
        vtx_new : VertexItem
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


class CmdRemoveSegment(CmdSceneBase):
    """Remove a specified segment from the scene."""

    # instance attributes
    _vtx1 : VertexItem
    _vtx2 : VertexItem
    _seg  : SegmentItem

    def __init__(
        self : Self,
        scene : "DrawingScene",
        seg : SegmentItem
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
