from __future__ import annotations

from typing import Self

from .....app import settings

from typing import TYPE_CHECKING
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
        from . import DiagramScene
        if not isinstance(self, DiagramScene): raise TypeError("Bad host")
        from ...items.mixin.handle import ItemHandlesMixin
        self.hideGrips()
        self._grip_items = [i for i in self.selectedItems() \
                if isinstance(i, ItemHandlesMixin)]
        for item in self._grip_items:
            item.setGripsVisible(True)

    def hideGrips(self : Self) -> None:
        for item in self._grip_items:
            item.setGripsVisible(False)
        self._grip_items = []
