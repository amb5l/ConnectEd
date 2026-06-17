from typing import Self, TypeAlias

from PyQt6.QtCore    import QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtWidgets import QGraphicsItem

from .....app import logger

from .....core.check import checked
from .....core.xml   import toXmlStartElement, toXmlEndElement, fromXml

from ...xml import toXmlProperties, fromXmlProperties

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...properties import PropertiesMixin
    from ..mixin       import ItemMixin

MixinSelf = object  # runtime stub for @checked string annotations


class ItemXmlMixin:
    if TYPE_CHECKING:
        MixinSelf: TypeAlias = Self | ItemMixin | PropertiesMixin

    _CHILD_TAGS = frozenset({
        "GatePin", "BlockPin", "SymbolPin", "PropertyText"
    })

    def toXmlChildren(self : "MixinSelf", xw : QXmlStreamWriter) -> None:
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

    @checked
    def toXml(self : "MixinSelf", xw : QXmlStreamWriter) -> None:
        toXmlStartElement(xw, self.__class__.__name__.removesuffix("Item"))
        toXmlProperties(self, xw)
        self.toXmlChildren(xw)
        toXmlEndElement(xw)

    @checked
    def fromXmlChild(self : "MixinSelf", xr : QXmlStreamReader) -> bool:
        """Handle one child start element. Returns True if consumed."""
        from ...items.port_pin   import PortPinMixin
        from ...items.gate_pin   import GatePinItem
        from ...items.block_pin  import BlockPinItem
        from ...items.symbol_pin import SymbolPinItem
        from ..property_text     import PropertyTextItem
        pin_classes = {
            "GatePin"   : GatePinItem,
            "BlockPin"  : BlockPinItem,
            "SymbolPin" : SymbolPinItem,
        }
        tag = xr.name()
        if tag in pin_classes:
            child_cls : type[PortPinMixin] = pin_classes[tag]
            child_cls.fromXml(xr, self)
            return True
        if tag == "PropertyText":
            child : PropertyTextItem = PropertyTextItem.fromXml(xr, self)
            if child is not None:
                prop_name = child.name()
                self.properties.setText(prop_name, child)
            return True
        return False

    @checked
    def fromXmlChildren(self : "MixinSelf", xr : QXmlStreamReader) -> None:
        """Consume child elements until the parent's end element."""
        xml_item_name = self.__class__.__name__.removesuffix("Item")
        def dispatch(xr : QXmlStreamReader) -> None:
            if not self.fromXmlChild(xr):
                logger().warning(f"Unexpected child item: {xr.name()}")
            return None
        fromXml(
            xr,
            dict.fromkeys(self._CHILD_TAGS, dispatch),
            ptag=xml_item_name,
        )

    @staticmethod
    def fromXmlRefresh(instance : "MixinSelf") -> None:
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
        instance : Self = cls(**args)
        fromXmlProperties(instance, xr)
        if hasattr(instance, "onGeometryChanged"):
            instance.onGeometryChanged()
        if not (xr.isEndElement() and xr.name() == xml_item_name):
            instance.fromXmlChildren(xr)
        ItemXmlMixin.fromXmlRefresh(instance)
        if hasattr(instance, "properties"):
            instance.properties.setNotify(True)  # enable property change signalling
        return instance
