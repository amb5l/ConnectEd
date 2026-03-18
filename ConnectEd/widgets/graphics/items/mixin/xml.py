from typing import Self

from PyQt6.QtCore    import QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtWidgets import QGraphicsItem

from .....app import logger

from .....core.xml   import toXmlAttrs, fromXmlAttrs
from .....core.utils import registerClass

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...properties   import PropertiesMixin
    from ..mixin         import ItemMixin
    from ..property_text import PropertyTextItem


class ItemXmlMixin:
    def toXmlBegin(self : Self, xw : QXmlStreamWriter) -> None:
        xw.writeStartElement(self.__class__.__name__.removesuffix("Item"))

    def toXmlAttrs(self : Self, xw : QXmlStreamWriter) -> None:
        toXmlAttrs(self, xw)

    def toXmlChildren(self : Self, xw : QXmlStreamWriter) -> None:
        from ..property_text import PropertyTextItem
        from ..base_pin      import BasePinItem
        from ..handle        import HandleItem
        for child in self.childItems():
            if isinstance(child, BasePinItem):
                child.toXml(xw)
            elif isinstance(child, HandleItem):
                for handle_child in child.childItems():
                    if isinstance(handle_child, PropertyTextItem):
                        handle_child.toXml(xw)

    def toXmlEnd(self : Self, xw : QXmlStreamWriter) -> None:
        xw.writeEndElement()

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        self.toXmlBegin(xw)
        self.toXmlAttrs(xw)
        self.toXmlChildren(xw)
        self.toXmlEnd(xw)

    @classmethod
    def fromXml(
        cls    : Self,
        xr     : QXmlStreamReader,
        parent : QGraphicsItem | None = None
    ) -> Self:
        xml_item_name = cls.__name__.removesuffix("Item")
        instance : "ItemMixin | PropertiesMixin" = cls(fresh=False, parent=parent)
        fromXmlAttrs(instance, xr)
        if hasattr(instance, "onGeometryChange"):
            instance.onGeometryChange()
        # check if we're already at the end element (self-closing)
        if xr.isEndElement() and xr.name() == xml_item_name:
            return instance
        # import and register child pin and property text items
        pkg = "ConnectEd.widgets.graphics.items"
        pin_classes = {}
        registerClass( pin_classes , "GatePinItem"   , pkg=pkg )
        registerClass( pin_classes , "BlockPinItem"  , pkg=pkg )
        registerClass( pin_classes , "SymbolPinItem" , pkg=pkg )
        from ..property_text import PropertyTextItem
        # process child items
        while not (xr.isEndElement() and xr.name() == xml_item_name):
            if xr.isStartElement():
                item_name = xr.name() + "Item"
                if item_name in pin_classes:
                    child_cls = pin_classes[item_name]
                    child = child_cls.fromXml(xr, instance)
                elif item_name == "PropertyTextItem":
                    child : "PropertyTextItem" = PropertyTextItem.fromXml(
                        xr, instance
                    )
                    prop_name = child.name()
                    if instance.hasProperty(prop_name):
                        instance.setPropertyText(prop_name, child)
                    else:
                        logger().warning(f"Property '{prop_name}' not found")
                    child.onTextChange()
                    child.onSceneRotationChange()
                else:
                    logger().warning(f"Unexpected child item: {xr.name()}")
            xr.readNext()
        return instance
