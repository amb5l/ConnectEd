from __future__ import annotations

from typing import Self, cast

from PyQt6.QtWidgets import QGraphicsItem

from .....core.check import checked

from ..protocols import FreshItemConstructor

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...properties import PropertiesManager, PropertiesMixin
    from .handle import ItemHandlesMixin


class ItemCloneMixin:

    # external instance attributes
    properties : PropertiesManager  # provided by PropertiesMixin

    @checked
    def clone(self : Self) -> Self:
        """Create a clone of this item with a new UUID."""
        from ...properties   import PropertiesMixin
        from ..handle        import HandleItem
        from ..property_text import PropertyTextItem
        from ..port_pin      import PortPinLineItem, PortPinPathItem
        from .handle         import ItemHandlesMixin
        if not isinstance(self, QGraphicsItem):
            raise TypeError("Bad host")
        constructor = cast(FreshItemConstructor[Self], self.__class__)
        clone_item = constructor(fresh=False)
        if not isinstance(clone_item, QGraphicsItem):
            raise TypeError("Bad clone")
        # clone properties
        if hasattr(self, "properties"):
            for name in self.properties.names():
                if self.properties.inherent(name):
                    value = self.properties.value(name)
                    if value is not None:
                        clone_item.properties.setValue(name, value)
                else:
                    kind = self.properties.kind(name)
                    value = self.properties.value(name)
                    if kind is not None:
                        clone_item.properties.add(name, kind, value)
        # clone property texts and pins
        for source_child in self.childItems():
            if isinstance(source_child, PortPinLineItem | PortPinPathItem):
                clone_pin = source_child.clone()
                clone_pin.setParentItem(clone_item)
            elif isinstance(source_child, HandleItem):
                for source_h_child in source_child.childItems():
                    if  isinstance(source_h_child, PropertyTextItem) \
                    and isinstance(clone_item, ItemHandlesMixin):
                        clone_pt = source_h_child.clone()
                        clone_pt.setParentItem(
                            clone_item.handles().get(source_child.id())
                        )
                        if isinstance(clone_item, PropertiesMixin):
                            name = source_h_child.name()
                            if name is not None:
                                clone_item.properties.setText(name, clone_pt)
        self._cloneAfter(cast(Self, clone_item))
        if isinstance(clone_item, PropertiesMixin):
            clone_item.setLive(True)  # enable property change signalling
        return clone_item

    def _cloneAfter(self, clone) -> None:
        """Hook for subclasses to copy geometry not covered by properties."""
        pass
