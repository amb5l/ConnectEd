from typing import Self

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...properties import PropertiesMixin, PropertySpec
    from .. import ItemMixin
    from .handle import ItemHandlesMixin
    ItemType = ItemMixin | ItemHandlesMixin | PropertiesMixin


class ItemCloneMixin:
    def clone(self : Self, original : Self | None = None) -> Self:
        """Create a clone of this or specified item with a new UUID."""
        from ..handle        import Handle
        from ..property_text import PropertyTextMixin
        from ..base_pin      import BasePin
        source : "ItemType" = original if original is not None else self
        clone : "ItemType" = self.__class__(bare=True)
        # clone properties
        if hasattr(self, "properties"):
            clone._property_specs = self._properties.copy()
            for pn in clone._property_specs:
                clone_ps = clone._property_specs[pn]
                source_ps = source._property_specs[pn]
                if isinstance(clone_ps, PropertySpec):
                    if source_ps.exists(source):
                        clone_ps.setter(clone, source_ps.getter(source))
                else:
                    clone_ps.value = source_ps.value
        # clone property texts and pins
        for source_child in source.childItems():
            if isinstance(source_child, BasePin):
                clone_pin = source_child.clone()
                clone_pin.setParentItem(clone)
            elif isinstance(source_child, Handle):
                for source_ap_child in source_child.childItems():
                    if isinstance(source_ap_child, PropertyTextMixin):
                        clone_ap_child = source_ap_child.clone()
                        clone_ap_child.setParentItem(
                            clone._handles[source_child.name()]
                        )
        return clone
