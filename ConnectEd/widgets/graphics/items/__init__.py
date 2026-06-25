from PyQt6.QtWidgets import QGraphicsItem

from ....app import logger

from ....core.utils import registerClass

from .mixin import ItemMixin

# Runtime union so isinstance(..., ItemType) works (e.g. property_text.item()).
ItemType = ItemMixin | QGraphicsItem


def clone(items : list["ItemMixin"]) -> list["ItemMixin"]:
    r = []
    for item in items:
        try:
            r.append(item.clone())
        except Exception as e:
            logger().warning(f"Failed to clone item {item}: {e}")
    return r
