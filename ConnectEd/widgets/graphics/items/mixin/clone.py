from typing import Self

from ...properties import PropertiesMixin, PropertySpec

from .. import ElementMixin

from .anchor import ElementAnchorPointsMixin


ElementType = ElementMixin | ElementAnchorPointsMixin | PropertiesMixin

class ElementCloneMixin:
    def clone(self : Self, original : Self | None = None) -> Self:
        """Create a clone of this or specified element with a new UUID."""
        from ..anchor_point  import AnchorPoint
        from ..property_text import PropertyText
        from ..pin           import Pin
        source : ElementType = original if original is not None else self
        clone : ElementType = self.__class__(bare=True)
        # clone properties
        if hasattr(self, "_properties"):
            clone._properties = self._properties.copy()
            for pn in clone._properties:
                clone_ps = clone._properties[pn]
                source_ps = source._properties[pn]
                if isinstance(clone_ps, PropertySpec):
                    clone_ps.setter(clone, source_ps.getter(source))
                else:
                    clone_ps.value = source_ps.value
        # clone property texts and pins
        for source_child in source.childItems():
            if isinstance(source_child, Pin):
                clone_pin = source_child.clone()
                clone_pin.setParentItem(clone)
            elif isinstance(source_child, AnchorPoint):
                for source_ap_child in source_child.childItems():
                    if isinstance(source_ap_child, PropertyText):
                        clone_ap_child = source_ap_child.clone()
                        clone_ap_child.setParentItem(
                            clone._anchor_points[source_child.name()]
                        )
        return clone
