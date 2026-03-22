from PyQt6.QtCore import QPointF

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...items import ItemMixin
    from . import DrawingScene


class DrawingSceneApiPrivateMixin:
    def _itemTypes(self : "DrawingScene", pos : QPointF) -> list[type]:
        items = self.items(pos)
        types = {item.__class__ for item in items}  # use a set to avoid duplicates
        return list(types)

    def _selectedTopItems(self : "DrawingScene") -> list["ItemMixin"]:
        """Returns selected items that are Items, and are not children."""
        return [
            item for item in self.selectedItems()
            if isinstance(item, "ItemMixin") and not item.parentItem()
        ]

    def _selectedItems(self : "DrawingScene") -> list["ItemMixin"]:
        """Returns selected items that are Items (includes children)."""
        return [
            item for item in self.selectedItems()
            if isinstance(item, "ItemMixin")
        ]

    def _snap(self : "DrawingScene", pos : QPointF, snap : QPointF) -> QPointF:
        return QPointF(
                round(pos.x() / snap.x()) * snap.x(),
                round(pos.y() / snap.y()) * snap.y()
            )
