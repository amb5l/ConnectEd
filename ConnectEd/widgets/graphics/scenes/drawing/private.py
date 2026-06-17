from typing import Self

from PyQt6.QtCore import QPointF

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...items import ItemMixin
    from . import DrawingScene
    MixinSelf = Self | DrawingScene


class DrawingSceneApiPrivateMixin:
    def _itemTypes(self : "MixinSelf", pos : QPointF) -> list[type]:
        items = self.items(pos)
        types = {item.__class__ for item in items}  # use a set to avoid duplicates
        return list(types)

    def _selectedTopItems(self : "MixinSelf") -> list["ItemMixin"]:
        """Returns selected items that are Items, and are not children."""
        from ...items import ItemMixin
        return [
            item for item in self.selectedItems()
            if isinstance(item, ItemMixin) and not item.parentItem()
        ]

    def _selectedItems(self : "MixinSelf") -> list["ItemMixin"]:
        """Returns selected items that are Items (includes children)."""
        from ...items import ItemMixin
        return [
            item for item in self.selectedItems()
            if isinstance(item, ItemMixin)
        ]

    def _snap(self : "MixinSelf", pos : QPointF, snap : QPointF) -> QPointF:
        return QPointF(
                round(pos.x() / snap.x()) * snap.x(),
                round(pos.y() / snap.y()) * snap.y()
            )
