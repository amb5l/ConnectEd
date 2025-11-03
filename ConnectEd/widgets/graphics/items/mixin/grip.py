from typing import Self


class ItemGripMixin:
    def setGripsVisible(self : Self, visible : bool) -> None:
        from ..polyline import Polyline
        from .anchor import ItemAnchorPointsMixin
        if isinstance(self, Polyline):
            # In vertex-edit mode (selMode==1), show vertices; otherwise hide them
            vtx_visible = visible and self.selMode() == 1
            for vertex in self._vertices:
                vertex.setVisible(vtx_visible)
            for segment in self._segments:
                segment.setVisible(vtx_visible)
            # Hide anchor points when in vertex-edit mode
            visible = visible and not self.selMode()
        if isinstance(self, ItemAnchorPointsMixin):
            for ap in self._anchor_points.values():
                ap._grip.setVisible(visible)
