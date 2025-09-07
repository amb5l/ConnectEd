from PyQt6.QtCore import QPointF

from ...items import ElementMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import DrawingScene


class DrawingSceneApiPrivateMixin:
    def _selectedTopElements(self : "DrawingScene") -> list[ElementMixin]:
        """Returns selected items that are Elements, and are not children."""
        return [
            item for item in self.selectedItems()
            if isinstance(item, ElementMixin) and not item.parentItem()
        ]

    def _selectedElements(self : "DrawingScene") -> list[ElementMixin]:
        """Returns selected items that are Elements (includes children)."""
        return [
            item for item in self.selectedItems()
            if isinstance(item, ElementMixin)
        ]

    def _snap(self : "DrawingScene", pos : QPointF, snap : QPointF) -> QPointF:
        return QPointF(
                round(pos.x() / snap.x()) * snap.x(),
                round(pos.y() / snap.y()) * snap.y()
            )
