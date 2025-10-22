from typing import Self

from PyQt6.QtCore import QXmlStreamWriter, QXmlStreamReader

from .....app import logger

from .....core.xml import toXmlAttrs, fromXmlAttrs


class ItemXmlMixin:
    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        from ..property_text import PropertyText
        from ..pin           import Pin
        from ..anchor_point  import AnchorPoint
        xw.writeStartElement(self.__class__.__name__)
        toXmlAttrs(self, xw)
        for child in self.childItems():
            if isinstance(child, Pin):
                child.toXml(xw)
            elif isinstance(child, AnchorPoint):
                for anchor_child in child.childItems():
                    if isinstance(anchor_child, PropertyText):
                        anchor_child.toXml(xw)
        xw.writeEndElement()

    @classmethod
    def fromXml(cls : Self, xr : QXmlStreamReader) -> Self:
        from ..property_text import PropertyText
        from ..block_pin     import BlockPin, BlockPinName, BlockPinComment
        from ..symbol_pin    import SymbolPin, SymbolPinName, SymbolPinComment
        instance = cls(bare=True)
        fromXmlAttrs(instance, xr)
        instance.onGeometryChange()
        # check if we're already at the end element (self-closing)
        if xr.isEndElement() and xr.name() == cls.__name__:
            return instance
        # read child pin and PropertyText items
        pin_classes = {
            "BlockPin"  : BlockPin,
            "SymbolPin" : SymbolPin
        }
        property_text_classes = {
            "PropertyText"     : PropertyText,
            "BlockPinName"     : BlockPinName,
            "BlockPinComment"  : BlockPinComment,
            "SymbolPinName"    : SymbolPinName,
            "SymbolPinComment" : SymbolPinComment
        }
        while not (xr.isEndElement() and xr.name() == cls.__name__):
            if xr.isStartElement():
                item_name = xr.name()
                if item_name in pin_classes:
                    child_cls = pin_classes[item_name]
                    child = child_cls.fromXml(xr)
                    child.setParentItem(instance)
                    child.onGeometryChange()
                elif item_name in property_text_classes:
                    child_cls = property_text_classes[item_name]
                    child = child_cls.fromXml(xr)
                    child.setParentItem(instance._anchor_points[child.cleat()])
                    child.onGeometryChange()
                else:
                    logger().warning(f"Unexpected child element: {item_name}")
            xr.readNext()
        return instance
