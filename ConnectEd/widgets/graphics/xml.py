# XML support functions for graphics scenes and items

from __future__ import annotations

from PyQt6.QtCore    import QXmlStreamReader, QXmlStreamWriter

from ...core.check import checked
from ...core.utils import space2underscore, underscore2space, val2str

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
