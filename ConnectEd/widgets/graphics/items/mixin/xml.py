from __future__ import annotations

from typing import Self, Any, cast

from PyQt6.QtCore    import QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtWidgets import QGraphicsItem

from .....app import logger

from .....core.check import checked
from .....core.xml   import toXmlStartElement, toXmlEndElement, fromXml

from ...properties import PropertiesMixin

from ...xml import toXmlProperties, fromXmlProperties

from ..protocols import (
    OnGeometryChangedProtocol,
    OnTextChangedProtocol,
    OnSceneOrientationChangedProtocol
)


class ItemXmlMixin:

    _XML_CHILDREN : frozenset[str] = frozenset({})

    @classmethod
    def xmlTag(cls : type[Self]) -> str:
        tag = cls.__name__.removesuffix("Item")
        tag = tag.removesuffix("Definition")
        tag = tag.removesuffix("Instance")
        return tag

    def toXmlBegin(self : Self, xw : QXmlStreamWriter) -> None:
        tag = type(self).xmlTag()
        toXmlStartElement(xw, tag)
        if isinstance(self, PropertiesMixin):
            toXmlProperties(self, xw)

    def toXmlEnd(self : Self, xw : QXmlStreamWriter) -> None:
        toXmlEndElement(xw)

    def toXmlChildren(
        self : Self,
        xw   : QXmlStreamWriter,
        *,
        pins : bool = True
    ) -> None:
        from ..property_text import PropertyTextItem
        from ..port_pin      import PortPinMixin
        from ..handle        import HandleItem
        if not isinstance(self, QGraphicsItem):
            raise TypeError("Bad host")
        for child in self.childItems():
            if pins and isinstance(child, PortPinMixin):
                child.toXml(xw)
            elif isinstance(child, HandleItem):
                for handle_child in child.childItems():
                    if isinstance(handle_child, PropertyTextItem):
                        handle_child.toXml(xw)

    @checked
    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        self.toXmlBegin(xw)
        self.toXmlChildren(xw)
        self.toXmlEnd(xw)

    @checked
    def fromXmlChild(self : Self, xr : QXmlStreamReader) -> bool:
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
        # dict[str, type] — typeguard Protocol check rejects classmethod fromXml
        # as an "instance method" when values are annotated as type[FromXmlProtocol].
        _child_items_xref : dict[str, type] = {
            "GatePin"   : GatePinItem,
            "BlockPin"  : BlockPinItem,
            "SymbolPin" : SymbolPinItem,
            "Line"      : LineItem,
            "Rectangle" : RectangleItem,
            "Ellipse"   : EllipseItem,
            "Polyline"  : PolylineItem,
            "Text"      : TextItem
        }
        if not isinstance(self, QGraphicsItem) \
        or not isinstance(self, PropertiesMixin):
            raise TypeError("Bad host")
        tag = xr.name()
        if tag == "PropertyText":
            pt = PropertyTextItem.fromXml(xr, self)
            if pt is not None:
                prop_name = pt.name()
                if isinstance(prop_name, str):
                    self.properties.setText(prop_name, pt)
            return True
        elif tag in _child_items_xref:
            child_cls = _child_items_xref[tag]
            child = child_cls.fromXml(xr)
            child.setParentItem(self)
            return True
        return False

    @checked
    def fromXmlChildren(self : Self, xr : QXmlStreamReader) -> None:
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
    def fromXmlRefresh(instance : object) -> None:
        if isinstance(instance, OnTextChangedProtocol):
            instance.onTextChanged()
        if isinstance(instance, OnSceneOrientationChangedProtocol):
            instance.onSceneOrientationChanged()
        if isinstance(instance, PropertiesMixin):
            for name in instance.properties.names():
                pt = instance.properties.text(name)
                if pt is not None and isinstance(pt, OnGeometryChangedProtocol):
                    pt.onGeometryChanged()

    @classmethod
    @checked
    def fromXml(
        cls    : type[Self],
        xr     : QXmlStreamReader,
        parent : QGraphicsItem | None = None
    ) -> Self:
        tag = cls.xmlTag()
        args : dict[str, Any] = {"fresh": False}
        if parent is not None:
            args["parent"] = parent
        instance = cls(**args)
        if isinstance(instance, PropertiesMixin):
            fromXmlProperties(instance, xr)
        if isinstance(instance, OnGeometryChangedProtocol):
            instance.onGeometryChanged()
        if not (xr.isEndElement() and xr.name() == tag):
            instance.fromXmlChildren(xr)
        ItemXmlMixin.fromXmlRefresh(instance)
        if isinstance(instance, PropertiesMixin):
            instance.setLive(True)
        return instance
