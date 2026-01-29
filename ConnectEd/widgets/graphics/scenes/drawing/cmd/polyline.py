from typing import Self

from PyQt6.QtCore import QPointF

from ....items.polyline import PolylineItem, PolyVtxItem

from . import CmdBase


class CmdPolyVtxBase(CmdBase):
    """Base class for all commands that work with a polyline vertex."""

    # instance attributes
    _polyline : PolylineItem
    _vtx      : PolyVtxItem | None

    def __init__(
        self     : Self,
        polyline : PolylineItem
    ):
        super().__init__()
        self._polyline = polyline
        self._vtx = None


class CmdAddPolyVtx(CmdPolyVtxBase):
    """Command to add a vertex to a polyline."""

    # instance attributes
    _pos   : QPointF
    _sweep : float | None

    def __init__(
        self     : Self,
        polyline : PolylineItem,
        pos      : QPointF,
        sweep    : float | None = None
    ):
        super().__init__(polyline)
        self._pos = pos
        self._sweep = sweep

    def redo(self : Self) -> None:
        self._vtx = self._polyline.addVertex(self._pos, self._sweep)

    def undo(self : Self) -> None:
        self._polyline.delLastVertex()
        self._vtx = None

    def vtx(self : Self) -> PolyVtxItem | None:
        return self._vtx
