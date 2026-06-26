# XML support functions for graphics scenes and items

from __future__ import annotations

from PyQt6.QtCore    import QPointF, QXmlStreamReader, QXmlStreamWriter

from ...core.check import checked
from ...core.utils import space2underscore, underscore2space, val2str
from ...core.xml   import copyXml, pasteXml, XmlProtocol

from .properties import PropertiesMixin


def toXmlProperties(instance : PropertiesMixin, xw : QXmlStreamWriter) -> None:
    for name in instance.properties.names():
        if not instance.properties.worthy(name):
            continue
        value = instance.properties.value(name)
        xw.writeAttribute(space2underscore(name), val2str(value))


@checked
def fromXmlProperties(
    instance : PropertiesMixin,
    xr       : QXmlStreamReader
) -> None:
    for xml_attr in xr.attributes():
        instance.properties.init(
            underscore2space(xml_attr.name()), xml_attr.value()
        )
    xr.readNext()

@checked
def copy(
    items : PropertiesMixin | list[PropertiesMixin],
    pos   : QPointF | None = None
) -> None:
    if not isinstance(items, list):
        items = [items]
    metadata = None
    if pos is not None:
        metadata = {"X" : val2str(pos.x()), "Y" : val2str(pos.y())}
    copyXml(items, metadata)


@checked
def paste(
    xref : dict[str, type[XmlProtocol]]
) -> tuple[list[XmlProtocol], dict[str, str]]:
    items, attributes = pasteXml(xref)
    x = attributes.get("X", None)
    y = attributes.get("Y", None)
    pos = None if x is None or y is None else QPointF(float(x), float(y))
    return items, pos
