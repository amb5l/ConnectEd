from typing import Self

from PyQt6.QtCore import QPointF

from ....items.polyline import Polyline, PolyVtx

from . import CmdBase


class CmdPolyVtxBase(CmdBase):
    """Base class for all commands that work with a polyline vertex."""

    # instance attributes
    _polyline : Polyline
    _vtx      : PolyVtx | None

    def __init__(
        self     : Self,
        polyline : Polyline
    ):
        super().__init__()
        self._polyline = polyline
        self._vtx = None


class CmdAddPolyVtx(CmdPolyVtxBase):
    """Command to add a vertex to a polyline."""

    # instance attributes
    _pos : QPointF

    def __init__(
        self     : Self,
        polyline : Polyline,
        pos      : QPointF
    ):
        super().__init__(polyline)
        self._pos = pos

    def redo(self : Self) -> None:
        print("Adding vertex to polyline")
        self._vtx = self._polyline.addVertex(self._pos)
        print("Vertex added to polyline - number =", self._polyline.vertexCount())

    def undo(self : Self) -> None:
        self._polyline.removeLastVertex()
        self._vtx = None

    def vtx(self : Self) -> PolyVtx | None:
        return self._vtx
