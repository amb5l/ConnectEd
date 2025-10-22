from .....app import settings

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import DrawingScene
    from ...items.mixin.anchor import ItemAnchorPointsMixin
    from ...items.mixin.origin import ItemOriginMixin


class DrawingSceneHandlesMixin:
    """Handle visibility."""

    # external instance attributes
    _handle_items : list["ItemAnchorPointsMixin | ItemOriginMixin"]

    def initHandle(self : "DrawingScene") -> None:
        self._handle_items = []
        settings().changed.connect(self.updateHandles)

    def updateHandles(self : "DrawingScene") -> None:
        self.hideHandles()
        self._handle_items = [i for i in self.selectedItems() \
                if hasattr(i, "_anchor_points")]
        for item in self._handle_items:
            for ap in item._anchor_points.values():
                ap._grip.setVisible(True)
            if hasattr(item, "_origin"):
                item._origin.setVisible(True)

    def hideHandles(self : "DrawingScene") -> None:
        for item in self._handle_items:
            for ap in item._anchor_points.values():
                ap._grip.setVisible(False)
            if hasattr(item, "_origin"):
                item._origin.setVisible(False)
        self._handle_items = []
