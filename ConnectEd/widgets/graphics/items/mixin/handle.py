from typing import Self

from .vertex import ItemVertexMixin


class ItemHandleMixin:
    def setHandlesVisible(self : Self, visible : bool) -> None:
        from .anchor import ItemAnchorPointsMixin
        if isinstance(self, ItemVertexMixin):
            for vertex in self._vertices:
                vertex.setVisible(visible and self.vertexEditMode())
                visible = visible and not self.vertexEditMode()
        if isinstance(self, ItemAnchorPointsMixin):
            for ap in self._anchor_points.values():
                ap._grip.setVisible(visible)
