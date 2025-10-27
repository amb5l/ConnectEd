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
        from ...items.mixin.anchor import ItemAnchorPointsMixin
        self.hideHandles()
        self._handle_items = [i for i in self.selectedItems() \
                if isinstance(i, ItemAnchorPointsMixin)]
        for item in self._handle_items:
            item.setHandlesVisible(True)

    def hideHandles(self : "DrawingScene") -> None:
        for item in self._handle_items:
            item.setHandlesVisible(False)
        self._handle_items = []
