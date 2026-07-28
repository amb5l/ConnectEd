from __future__ import annotations

from typing import Self

from .....app import settings

from typing import TYPE_CHECKING
from .host import asDiagramScene
if TYPE_CHECKING:
    from ...items.mixin.handle import ItemHandlesMixin


class DiagramSceneGripsMixin:
    """Grip visibility."""

    # external instance attributes
    _grip_items : list[ItemHandlesMixin]

    def initGrips(self : Self) -> None:
        self._grip_items = []
        settings().changed.connect(self.updateGrips)

    def updateGrips(self : Self) -> None:
        host = asDiagramScene(self)
        from ...items.mixin.handle import ItemHandlesMixin
        host.hideGrips()
        host._grip_items = [i for i in host.selectedItems() \
                if isinstance(i, ItemHandlesMixin)]
        for item in host._grip_items:
            item.setGripsVisible(True)

    def hideGrips(self : Self) -> None:
        for item in self._grip_items:
            item.setGripsVisible(False)
        self._grip_items = []
