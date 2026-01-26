from typing import Self

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...properties import PropertiesMixin
    from .. import ItemMixin
    from .handle import ItemHandlesMixin
    ItemType = ItemMixin | ItemHandlesMixin | PropertiesMixin


class ItemCloneMixin:
    def clone(self : Self, original : Self | None = None) -> Self:
        """Create a clone of this or specified item with a new UUID."""
        from ..handle        import HandleItem
        from ..property_text import PropertyTextItem
        from ..base_pin      import BasePinItem
        source : "ItemType" = original if original is not None else self
        clone_item : "ItemType" = self.__class__(fresh=False)
        # clone properties
        if hasattr(source, "properties"):
            for name, source_prop in source.properties.items():
                clone_item.properties[name] = source_prop.clone(clone_item)
        # clone property texts and pins
        for source_child in source.childItems():
            if isinstance(source_child, BasePinItem):
                clone_pin = source_child.clone()
                clone_pin.setParentItem(clone_item)
            elif isinstance(source_child, HandleItem):
                for source_ap_child in source_child.childItems():
                    if isinstance(source_ap_child, PropertyTextItem):
                        clone_ap_child = source_ap_child.clone()
                        clone_ap_child.setParentItem(
                            clone_item._handles[source_child.name()]
                        )
        return clone_item
