from typing import Self

from .....core.check import checked

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...properties import PropertiesMixin
    from .. import ItemMixin
    from .handle import ItemHandlesMixin
    ItemType = ItemMixin | ItemHandlesMixin | PropertiesMixin


class ItemCloneMixin:
    @checked
    def clone(self : Self, original : Self | None = None) -> Self:
        """Create a clone of this item with a new UUID."""
        from ..handle        import HandleItem
        from ..property_text import PropertyTextItem
        from ..port_pin      import PortPinLineItem, PortPinPathItem
        source : "ItemType" = original if original is not None else self
        clone_item : "ItemType" = self.__class__(fresh=False)
        # clone properties
        if hasattr(source, "properties"):
            for name in source.properties.names():
                if source.properties.inherent(name):
                    value = source.properties.value(name)
                    if value is not None:
                        clone_item.properties.setValue(name, value)
                else:
                    kind = source.properties.kind(name)
                    value = source.properties.value(name)
                    if kind is not None:
                        clone_item.properties.add(name, kind, value)
        # clone property texts and pins
        for source_child in source.childItems():
            if isinstance(source_child, PortPinLineItem | PortPinPathItem):
                clone_pin = source_child.clone()
                clone_pin.setParentItem(clone_item)
            elif isinstance(source_child, HandleItem):
                for source_ap_child in source_child.childItems():
                    if isinstance(source_ap_child, PropertyTextItem):
                        clone_ap_child = source_ap_child.clone()
                        clone_ap_child.setParentItem(
                            clone_item._handles[source_child.id()]
                        )
                        if hasattr(clone_item, "properties"):
                            clone_item.properties.setText(
                                source_ap_child.name(),
                                clone_ap_child,
                            )
        self._cloneAfter(source, clone_item)
        if hasattr(clone_item, "properties"):
            clone_item.setLive(True)  # enable property change signalling
        return clone_item

    def _cloneAfter(
        self        : Self,
        source      : "ItemType",
        clone_item  : "ItemType",
    ) -> None:
        """Hook for subclasses to copy geometry not covered by properties."""
        pass
