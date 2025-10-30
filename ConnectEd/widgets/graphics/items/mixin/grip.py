from typing import Self


class ItemGripMixin:
    def setGripsVisible(self : Self, visible : bool) -> None:
        from ..polyline import Polyline
        from .anchor import ItemAnchorPointsMixin
        if isinstance(self, Polyline):
            for vertex in self._vertices:
                vertex.setVisible(visible and self.selMode())
                visible = visible and not self.selMode()
        if isinstance(self, ItemAnchorPointsMixin):
            for ap in self._anchor_points.values():
                ap._grip.setVisible(visible)
