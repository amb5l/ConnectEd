from .....app import settings

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import DrawingScene
    from ...items.mixin.anchor import ItemAnchorPointsMixin
    from ...items.mixin.origin import ItemOriginMixin


class DrawingSceneGripsMixin:
    """Grip visibility."""

    # external instance attributes
    _grip_items : list["ItemAnchorPointsMixin | ItemOriginMixin"]

    def initGrips(self : "DrawingScene") -> None:
        self._grip_items = []
        settings().changed.connect(self.updateGrips)

    def updateGrips(self : "DrawingScene") -> None:
        from ...items.mixin.anchor import ItemAnchorPointsMixin
        self.hideGrips()
        self._grip_items = [i for i in self.selectedItems() \
                if isinstance(i, ItemAnchorPointsMixin)]
        for item in self._grip_items:
            item.setGripsVisible(True)

    def hideGrips(self : "DrawingScene") -> None:
        for item in self._grip_items:
            item.setGripsVisible(False)
        self._grip_items = []
