from __future__ import annotations

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
    MixinSelf: TypeAlias = Self | ItemMixin | PropertiesMixin
else:
    MixinSelf = Self


class ItemXmlMixin:
    _XML_CHILDREN : frozenset[str] = frozenset({})

    @classmethod
    def xmlTag(cls : type[MixinSelf]) -> str:
        tag = cls.__name__.removesuffix("Item")
        tag = tag.removesuffix("Definition")
        tag = tag.removesuffix("Instance")
        return tag

    def toXmlBegin(self : MixinSelf, xw : QXmlStreamWriter) -> None:
        tag = type(self).xmlTag()
        toXmlStartElement(xw, tag)
        if hasattr(self, "properties"):
            toXmlProperties(self, xw)

    def toXmlEnd(self : MixinSelf, xw : QXmlStreamWriter) -> None:
        toXmlEndElement(xw)

    def toXmlChildren(
        self : MixinSelf,
        xw   : QXmlStreamWriter,
        *,
        pins : bool = True
    ) -> None:
        from ..property_text import PropertyTextItem
        from ..port_pin      import PortPinMixin
        from ..handle        import HandleItem
        for child in self.childItems():
            if pins and isinstance(child, PortPinMixin):
                child.toXml(xw)
            elif isinstance(child, HandleItem):
                for handle_child in child.childItems():
                    if isinstance(handle_child, PropertyTextItem):
                        handle_child.toXml(xw)

    @checked
    def toXml(self : MixinSelf, xw : QXmlStreamWriter) -> None:
        self.toXmlBegin(xw)
        self.toXmlChildren(xw)
        self.toXmlEnd(xw)

    @checked
    def fromXmlChild(self : MixinSelf, xr : QXmlStreamReader) -> bool:
        """Handle one child start element. Returns True if consumed."""
        from ..property_text     import PropertyTextItem
        from ...items.gate_pin   import GatePinItem
        from ...items.block_pin  import BlockPinItem
        from ...items.symbol_pin import SymbolPinItem
        from ...items.line       import LineItem
        from ...items.rectangle  import RectangleItem
        from ...items.ellipse    import EllipseItem
        from ...items.polyline   import PolylineItem
        from ...items.text       import TextItem
        _item_classes = {
            "GatePin"   : GatePinItem,
            "BlockPin"  : BlockPinItem,
            "SymbolPin" : SymbolPinItem,
            "Line"      : LineItem,
            "Rectangle" : RectangleItem,
            "Ellipse"   : EllipseItem,
            "Polyline"  : PolylineItem,
            "Text"      : TextItem
        }
        tag = xr.name()
        if tag == "PropertyText":
            pt : PropertyTextItem = PropertyTextItem.fromXml(xr, self)
            if pt is not None:
                prop_name = pt.name()
                self.properties.setText(prop_name, pt)
            return True
        elif tag in _item_classes:
            child_cls : type[ItemXmlMixin] = _item_classes[tag]
            child = child_cls.fromXml(xr)
            child.setParentItem(self)
            return True
        return False

    @checked
    def fromXmlChildren(self : MixinSelf, xr : QXmlStreamReader) -> None:
        """Consume child elements until the parent's end element."""
        tag = type(self).xmlTag()
        def dispatch(xr : QXmlStreamReader) -> None:
            if not self.fromXmlChild(xr):
                logger().warning(f"Unexpected child item: {xr.name()}")
            return None
        fromXml(
            xr,
            dict.fromkeys(self._XML_CHILDREN, dispatch),
            ptag=tag,
        )

    @staticmethod
    def fromXmlRefresh(instance : MixinSelf) -> None:
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
        cls    : MixinSelf,
        xr     : QXmlStreamReader,
        parent : QGraphicsItem | None = None
    ) -> Self:
        tag = cls.xmlTag()
        args = {"fresh": False}
        if parent is not None:
            args["parent"] = parent
        instance : MixinSelf = cls(**args)
        fromXmlProperties(instance, xr)
        if hasattr(instance, "onGeometryChanged"):
            instance.onGeometryChanged()
        if not (xr.isEndElement() and xr.name() == tag):
            instance.fromXmlChildren(xr)
        ItemXmlMixin.fromXmlRefresh(instance)
        if hasattr(instance, "properties"):
            instance.setLive(True)
        return instance
