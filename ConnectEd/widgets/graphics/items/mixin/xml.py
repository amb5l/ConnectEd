from typing import Self

from PyQt6.QtCore import QXmlStreamWriter, QXmlStreamReader

from .....core.log import logger
from .....core.xml import toXmlAttrs, fromXmlAttrs


class ElementXmlMixin:
    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        from ..property_text import PropertyText
        from ..port_pin      import BasePin
        xw.writeStartElement(self.__class__.__name__)
        toXmlAttrs(self, xw)
        from ..port_pin import BasePin
        for child in self.childItems():
            if isinstance(child, PropertyText | BasePin):
                child.toXml(xw)
        xw.writeEndElement()

    @classmethod
    def fromXml(cls : Self, xr: QXmlStreamReader) -> Self:
        from ..property_text import PropertyText
        from ..port_pin      import BlockPin
        instance = cls(bare=True)
        fromXmlAttrs(instance, xr)
        instance.onGeometryChange()
        # check if we're already at the end element (self-closing)
        if xr.isEndElement() and xr.name() == cls.__name__:
            return instance
        # read child PropertyText and pin elements
        while not (xr.isEndElement() and xr.name() == cls.__name__):
            if xr.isStartElement():
                if xr.name() == "BlockPin":
                    child = BlockPin.fromXml(xr)
                    child.setParentItem(instance)
                elif xr.name() == "PropertyText":
                    child : PropertyText = PropertyText.fromXml(xr)
                    child.setParentItem(instance._anchor_points[child._origin()])
                else:
                    logger.warning(f"Unexpected child element: {xr.name()}")
                    continue
            xr.readNext()
        return instance
