from typing import Self, TypeAlias

from .....app import settings

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import DrawingScene
    from ...items.mixin.handle import ItemHandlesMixin
    MixinSelf: TypeAlias = Self | DrawingScene
else:
    MixinSelf = object

class DrawingSceneGripsMixin:
    """Grip visibility."""

    # external instance attributes
    _grip_items : list[ItemHandlesMixin]

    def initGrips(self : MixinSelf) -> None:
        self._grip_items = []
        settings().changed.connect(self.updateGrips)

    def updateGrips(self : MixinSelf) -> None:
        from ...items.mixin.handle import ItemHandlesMixin
        self.hideGrips()
        self._grip_items = [i for i in self.selectedItems() \
                if isinstance(i, ItemHandlesMixin)]
        for item in self._grip_items:
            item.setGripsVisible(True)

    def hideGrips(self : MixinSelf) -> None:
        for item in self._grip_items:
            item.setGripsVisible(False)
        self._grip_items = []
