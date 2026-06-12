from typing import Self

from PyQt6.QtCore    import QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtWidgets import QGraphicsItem

from .....app import logger

from .....core.check import checked
from .....core.xml import toXmlAttrs, fromXmlAttrs

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...properties import PropertiesMixin
    from ..mixin       import ItemMixin


class ItemXmlMixin:
    def toXmlBegin(self : Self, xw : QXmlStreamWriter) -> None:
        xw.writeStartElement(self.__class__.__name__.removesuffix("Item"))

    def toXmlAttrs(self : Self, xw : QXmlStreamWriter) -> None:
        toXmlAttrs(self, xw)

    def toXmlChildren(self : Self, xw : QXmlStreamWriter) -> None:
        from ..property_text import PropertyTextItem
        from ..port_pin      import PortPinMixin
        from ..handle        import HandleItem
        for child in self.childItems():
            if isinstance(child, PortPinMixin):
                child.toXml(xw)
            elif isinstance(child, HandleItem):
                for handle_child in child.childItems():
                    if isinstance(handle_child, PropertyTextItem):
                        handle_child.toXml(xw)

    def toXmlEnd(self : Self, xw : QXmlStreamWriter) -> None:
        xw.writeEndElement()

    @checked
    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        self.toXmlBegin(xw)
        self.toXmlAttrs(xw)
        self.toXmlChildren(xw)
        self.toXmlEnd(xw)

    @staticmethod
    def _fromXmlRefresh(instance : "ItemMixin | PropertiesMixin") -> None:
        if hasattr(instance, "onTextChanged"):
            instance.onTextChanged()
        if hasattr(instance, "onSceneRotationChanged"):
            instance.onSceneRotationChanged()
        if hasattr(instance, "properties"):
            for name in instance.properties.names():
                pt = instance.properties.text(name)
                if pt is not None and hasattr(pt, "onGeometryChanged"):
                    pt.onGeometryChanged()

    @classmethod
    @checked
    def fromXml(
        cls    : Self,
        xr     : QXmlStreamReader,
        parent : QGraphicsItem | None = None
    ) -> Self:
        xml_item_name = cls.__name__.removesuffix("Item")
        args = {"fresh": False}
        if parent is not None:
            args["parent"] = parent
        instance : "ItemMixin | PropertiesMixin" = cls(**args)
        fromXmlAttrs(instance, xr)
        if hasattr(instance, "onGeometryChanged"):
            instance.onGeometryChanged()
        if not (xr.isEndElement() and xr.name() == xml_item_name):
            # process child items
            from ...items.port_pin   import PortPinMixin
            from ...items.gate_pin   import GatePinItem
            from ...items.block_pin  import BlockPinItem
            from ...items.symbol_pin import SymbolPinItem
            from ..property_text     import PropertyTextItem
            pin_classes = {
                "GatePinItem"   : GatePinItem,
                "BlockPinItem"  : BlockPinItem,
                "SymbolPinItem" : SymbolPinItem
            }
            while not (xr.isEndElement() and xr.name() == xml_item_name):
                if xr.isStartElement():
                    item_name = xr.name() + "Item"
                    if item_name in pin_classes:
                        child_cls : type[PortPinMixin] = pin_classes[item_name]
                        child = child_cls.fromXml(xr, instance)
                    elif item_name == "PropertyTextItem":
                        child : PropertyTextItem = PropertyTextItem.fromXml(
                            xr, instance
                        )
                        if child is not None:
                            prop_name = child.name()
                            instance.properties.setText(prop_name, child)
                            ItemXmlMixin._fromXmlRefresh(child)
                    else:
                        logger().warning(f"Unexpected child item: {xr.name()}")
                xr.readNext()
        ItemXmlMixin._fromXmlRefresh(instance)
        if hasattr(instance, "properties"):
            instance.properties.setNotify(True)  # enable property change signalling
        return instance
