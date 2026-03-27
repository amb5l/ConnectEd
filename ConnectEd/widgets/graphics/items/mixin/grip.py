from typing import Self


class ItemGripMixin:
    def setGripsVisible(self : Self, visible : bool) -> None:
        from ..polyline import PolylineItem
        from .handle    import ItemHandlesMixin
        if isinstance(self, PolylineItem):
            # In vertex-edit mode (selMode==1), show vertices; otherwise hide them
            vtx_visible = visible and self.selMode() == 1
            for i, vertex in enumerate(self._vertices):
                vertex.setVisible((visible and i == 0) or vtx_visible)
            for segment in self._segments:
                segment.setVisible(vtx_visible)
            # Hide grips when in vertex-edit mode
            visible = visible and not self.selMode()
        if isinstance(self, ItemHandlesMixin):
            for h in self._handles.values():
                h._grip.setVisible(visible)
