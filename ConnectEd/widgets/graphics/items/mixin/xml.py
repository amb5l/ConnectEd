from typing import Self

from PyQt6.QtCore import QXmlStreamWriter, QXmlStreamReader

from .....app import logger

from .....core.xml   import toXmlAttrs, fromXmlAttrs
from .....core.utils import registerClass

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...properties   import PropertiesMixin
    from ..mixin         import ItemMixin
    from ..property_text import PropertyTextMixin


class ItemXmlMixin:
    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        from ..property_text import PropertyTextMixin
        from ..base_pin      import BasePin
        from ..handle        import Handle
        xw.writeStartElement(self.__class__.__name__)
        toXmlAttrs(self, xw)
        for child in self.childItems():
            if isinstance(child, BasePin):
                child.toXml(xw)
            elif isinstance(child, Handle):
                for handle_child in child.childItems():
                    if isinstance(handle_child, PropertyTextMixin):
                        handle_child.toXml(xw)
        xw.writeEndElement()

    @classmethod
    def fromXml(cls : Self, xr : QXmlStreamReader) -> Self:
        instance : "ItemMixin | PropertiesMixin" = cls(bare=True)
        fromXmlAttrs(instance, xr)
        if hasattr(instance, "onGeometryChange"):
            instance.onGeometryChange()
        # check if we're already at the end element (self-closing)
        if xr.isEndElement() and xr.name() == cls.__name__:
            return instance
        # import and registerchild pin and property text items
        pkg = "ConnectEd.widgets.graphics.items"
        pin_classes = {}
        registerClass( pin_classes , "GatePin"   , pkg=pkg )
        registerClass( pin_classes , "BlockPin"  , pkg=pkg )
        registerClass( pin_classes , "SymbolPin" , pkg=pkg )
        pt_classes = {}
        registerClass( pt_classes , "PropertyTextLine"  , "property_text" , pkg )
        registerClass( pt_classes , "PropertyTextBlock" , "property_text" , pkg )
        # process child items
        while not (xr.isEndElement() and xr.name() == cls.__name__):
            if xr.isStartElement():
                item_name = xr.name()
                if item_name in pin_classes:
                    child_cls = pin_classes[item_name]
                    child = child_cls.fromXml(xr)
                    child.setParentItem(instance)
                elif item_name in pt_classes:
                    child_cls = pt_classes[item_name]
                    child : "PropertyTextMixin" = child_cls.fromXml(xr)
                    child.setParentItem(instance.getHandle(child.getCleat()))
                    prop_name = child.property()
                    if prop_name in instance.properties:
                        instance.properties[prop_name].setText(child)
                    child.onTextChange()
                    if hasattr(child, 'onRotationChange'):
                        child.onRotationChange()
                else:
                    logger().warning(f"Unexpected child element: {item_name}")
            xr.readNext()
        return instance
