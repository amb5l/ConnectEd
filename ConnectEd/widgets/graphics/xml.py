# XML support functions for graphics scenes and items

from __future__ import annotations

from typing import Any

from PyQt6.QtCore import QXmlStreamReader, QXmlStreamWriter

from ...core.check import checked
from ...core.types import DataKind
from ...core.utils import space2underscore, underscore2space, val2str, str2val

from .properties import PropertiesMixin


@checked
def toXmlProperties(obj : PropertiesMixin, xw : QXmlStreamWriter) -> None:
    for name, property in obj.properties.items():
        if not property.worthy():
            continue
        value = property.value(raw = True)
        xw.writeAttribute(space2underscore(name), val2str(value))


@checked
def fromXmlProperties(obj : PropertiesMixin, xr  : QXmlStreamReader) -> None:
    for xml_attr in xr.attributes():
        name = underscore2space(xml_attr.name())
        raw  = xml_attr.value()
        if name in obj.properties:
            prop = obj.properties[name]
            kind = prop.kind()
            value : Any = raw
            if isinstance(raw, str) and kind not in (DataKind.STR, DataKind.TEXT):
                value = str2val(raw, kind.types()[0].__name__)
            prop.setValue(value)
        else:
            obj.propertyAdd(name, DataKind.STR, raw)
    xr.readNext()
