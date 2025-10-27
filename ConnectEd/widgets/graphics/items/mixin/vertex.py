from typing import Self

from PyQt6.QtCore import QPointF

from ..poly_vtx import PolyVtx

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .anchor import ItemVertexAnchorPointsMixin


class ItemVertexMixin:
    # instance attributes
    _vertices : list[PolyVtx]
    _vtx_edit : bool

    def initVertices(self : Self) -> None:
        self._vertices = [PolyVtx(self), PolyVtx(self)]
        self._vtx_edit = False

    def onSelectionChange(self : Self, selected : bool) -> None:
        if not selected:
            self._vtx_edit = False

    def setLastVertexPos(self : Self, pos : QPointF) -> None:
        """Set position of last vertex. Note: pos is in local coordinates."""
        self._vertices[-1].setPos(pos)
        self.updateVertices()

    def addVertex(self : "Self | ItemVertexAnchorPointsMixin", pos : QPointF) -> None:
        """Add a new vertex. Note: pos is in local coordinates."""
        self._vertices.append(PolyVtx(self, pos))
        self.updateVertices()

    def removeLastVertex(self : "Self | ItemVertexAnchorPointsMixin") -> None:
        """Remove the last vertex."""
        self._vertices.pop()
        self.updateVertices()

    def vertexEditMode(self : Self) -> bool:
        return self._vtx_edit

    def setVertexEditMode(self : Self, enable : bool) -> None:
        self._vtx_edit = enable

    def updateVertices(self : Self) -> None:
        raise NotImplementedError("Subclass must implement this method")
