from typing import TYPE_CHECKING

from ...items import ElementMixin

if TYPE_CHECKING:
    from .. import DrawingScene


class DrawingSceneApiPrivateMixin:
    def _selectedElements(self : "DrawingScene") -> list[ElementMixin]:
        """Returns selected items that are Elements, and are not children."""
        return [
            item for item in self.scene().selectedItems()
            if isinstance(item, ElementMixin) and not item.parent()
        ]
