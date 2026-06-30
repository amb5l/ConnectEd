from __future__ import annotations

from typing import Self

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QGraphicsItem

from ...items.role import ChromeItem


class DiagramScenePrivateMixin:
    def _itemTypes(self : Self, pos : QPointF) -> list[type]:
        from . import DiagramScene
        if not isinstance(self, DiagramScene): raise TypeError("Bad host")
        items = self.items(pos)
        types = {item.__class__ for item in items}  # use a set to avoid duplicates
        return list(types)

    def _topItems(
        self  : Self,
        items : QGraphicsItem | list[QGraphicsItem]
    ) -> list[QGraphicsItem]:
        if not isinstance(items, list):
            items = [items]
        return [
            item for item in items
            if not isinstance(item, ChromeItem) and item.parentItem() is None
        ]

    def _selectedTopItems(self : Self) -> list[QGraphicsItem]:
        """Returns selected items that are Items, and are not children."""
        return [
            item for item in self._selectedItems()
            if item.parentItem() is None
        ]

    def _selectedItems(self : Self) -> list[QGraphicsItem]:
        """Returns selected items that are Items (includes children)."""
        from . import DiagramScene
        if not isinstance(self, DiagramScene): raise TypeError("Bad host")
        return [
            item for item in self.selectedItems()
            if not isinstance(item, ChromeItem)
        ]

    def _snap(self : Self, pos : QPointF, snap : QPointF) -> QPointF:
        return QPointF(
                round(pos.x() / snap.x()) * snap.x(),
                round(pos.y() / snap.y()) * snap.y()
            )
