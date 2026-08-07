from __future__ import annotations

from typing import Self, cast

from PyQt6.QtWidgets import QGraphicsItem

from .....core.check import checked

from ..protocols import FreshItemConstructor


class ItemCloneMixin:
    @checked
    def clone(self : Self) -> Self:
        """Create a clone of this item with a new UUID."""
        from ..handle        import HandleItem
        from ..property_text import PropertyTextItem
        from ..port_pin      import PortPinLineItem, PortPinPathItem
        from .handle         import ItemHandlesMixin
        from .properties     import ItemPropertiesMixin
        if not isinstance(self, QGraphicsItem):
            raise TypeError("Bad host")
        constructor = cast(FreshItemConstructor[Self], self.__class__)
        clone_item = constructor(fresh=False), QGraphicsItem
        if not isinstance(clone_item, QGraphicsItem) \
        or not isinstance(clone_item, ItemPropertiesMixin):
            raise TypeError("Bad clone")
        # clone properties
        if isinstance(self, ItemPropertiesMixin):
            for name in self.propertyNames():
                if self.propertyInherent(name):
                    value = self.propertyValue(name)
                    if value is not None:
                        clone_item.setPropertyValue(name, value)
                else:
                    kind = self.propertyKind(name)
                    value = self.propertyValue(name)
                    if kind is not None:
                        clone_item.propertyAdd(name, kind, value)
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
                        name = source_h_child.name()
                        if name is not None:
                            clone_item.setPropertyTextItem(name, clone_pt)
        self._cloneAfter(cast(Self, clone_item))
        clone_item.setPropertiesLive(True)  # enable property change signalling
        return cast(Self, clone_item)

    def _cloneAfter(self, clone) -> None:
        """Hook for subclasses to copy geometry not covered by properties."""
        pass
