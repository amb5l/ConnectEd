from ...items import ElementMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingScene


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