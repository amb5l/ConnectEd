from __future__ import annotations

from typing import Self, cast, TYPE_CHECKING

from PyQt6.QtWidgets import QGraphicsItem

from .....core.check import checked

from ...properties import PropertiesMixin

from ..protocols import FreshItemConstructor

if TYPE_CHECKING:
    from ..property_text import PropertyTextItem


class ItemCloneMixin:
    @checked
    def clone(self : Self) -> Self:
        """Create a clone of this item with a new UUID."""
        from ..port_pin import PortPinLineItem, PortPinPathItem
        if not isinstance(self, QGraphicsItem):
            raise TypeError("Bad host")
        constructor = cast(FreshItemConstructor[Self], self.__class__)
        clone_item = constructor(fresh=False)
        if not isinstance(clone_item, QGraphicsItem):
            raise TypeError("Bad clone")
        # clone properties and their optional display texts
        if isinstance(self, PropertiesMixin):
            if not isinstance(clone_item, PropertiesMixin):
                raise TypeError("Bad clone")
            for name, source_property in self.properties.items():
                if source_property.isInherent():
                    clone_property = clone_item.properties[name]
                    clone_property.setValue(source_property.value())
                else:
                    clone_property = clone_item.propertyAdd(
                        name,
                        source_property.kind(),
                        source_property.value(raw = True)
                    )
                    if clone_property is None:
                        raise ValueError(
                            f"Failed to add property {name}"
                        )
                source_display_item = source_property.displayItem()
                if source_display_item is None:
                    continue
                dest_display_item = clone_property.setDisplay(True)
                if dest_display_item is None:
                    raise ValueError(
                        f"Display item for property {name} is None"
                    )
                _copyPropertyDisplay(source_display_item, dest_display_item)
        # clone pins (each pin clones its own properties and displays)
        for source_child in self.childItems():
            if isinstance(source_child, PortPinLineItem | PortPinPathItem):
                clone_pin = source_child.clone()
                clone_pin.setParentItem(clone_item)
        self._cloneAfter(clone_item)
        if isinstance(clone_item, PropertiesMixin):
            clone_item.setPropertiesLive(True)
        return cast(Self, clone_item)

    def _cloneAfter(self : Self, clone : ItemCloneMixin) -> None:
        """Hook for subclasses to copy geometry not covered by properties."""
        pass


def _copyPropertyDisplay(
    source : PropertyTextItem,
    dest   : PropertyTextItem,
) -> None:
    dest.setVisible       ( source.isVisible()     )
    dest.setCleat         ( source.cleat()         )
    dest.setPos           ( source.pos()           )
    dest.setRotation      ( source.rotation()      )
    dest.setMirrorH       ( source.mirrorH()       )
    dest.setMirrorV       ( source.mirrorV()       )
    dest.setAutoflip      ( source.autoflip()      )
    dest.setOrigin        ( source.origin()        )
    dest.setAlignH        ( source.alignH()        )
    dest.setAlignV        ( source.alignV()        )
    dest.setWidth         ( source.width()         )
    dest.setHeight        ( source.height()        )
    dest.setPadLeft       ( source.padLeft()       )
    dest.setPadRight      ( source.padRight()      )
    dest.setPadTop        ( source.padTop()        )
    dest.setPadBottom     ( source.padBottom()     )
    dest.setTextColor     ( source.textColor()     )
    dest.setTextFont      ( source.textFont()      )
    dest.setTextSize      ( source.textSize()      )
    dest.setTextBold      ( source.textBold()      )
    dest.setTextItalic    ( source.textItalic()    )
    dest.setTextUnderline ( source.textUnderline() )
