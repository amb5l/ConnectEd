# XML support functions for graphics scenes and items

from __future__ import annotations

from typing      import Any
from dataclasses import dataclass
from contextvars import ContextVar, Token

from PyQt6.QtCore import QXmlStreamReader, QXmlStreamWriter

from ...app import logger

from ...core.check import checked
from ...core.types import DataKind
from ...core.utils import space2underscore, underscore2space, val2str, str2val
from ...core.xml   import toXmlEndElement, toXmlStartElement

from .properties import PropertiesMixin, Property


# Position is required on every item, including the origin.
_ALWAYS_WRITTEN = frozenset({"X", "Y"})


@dataclass
class XmlDefaults:
    by_tag : dict[str, dict[str, str]]
    warned : set[tuple[str, str]]


_xml_defaults : ContextVar[XmlDefaults | None] = ContextVar(
    "xml_defaults",
    default=None,
)


def bindXmlDefaults(
    by_tag : dict[str, dict[str, str]],
) -> Token[XmlDefaults | None]:
    return _xml_defaults.set(XmlDefaults(by_tag=by_tag, warned=set()))


def unbindXmlDefaults(token : Token[XmlDefaults | None]) -> None:
    _xml_defaults.reset(token)


def _xmlTag(obj : object) -> str | None:
    xml_tag = getattr(type(obj), "xmlTag", None)
    if not callable(xml_tag):
        return None
    tag = xml_tag()
    if not isinstance(tag, str):
        return None
    return tag


@checked
def surveyXmlDefaults(
    items : list[PropertiesMixin],
) -> dict[str, dict[str, str]]:
    """
    Per tag, the attributes whose unworthy stored values are all identical.
    A tag with no such attribute is still present, mapped to an empty dict.
    """
    order   : list[str]                      = []
    omitted : dict[str, dict[str, set[str]]] = {}
    seen    : dict[str, list[str]]           = {}
    for item in items:
        tag = _xmlTag(item)
        if tag is None:
            continue
        if tag not in omitted:
            order.append(tag)
            omitted[tag] = {}
            seen[tag]    = []
        for name, prop in item.properties.items():
            if name in _ALWAYS_WRITTEN or prop.worthy():
                continue
            if name not in omitted[tag]:
                seen[tag].append(name)
                omitted[tag][name] = set()
            omitted[tag][name].add(val2str(prop.value(raw=True)))
    defaults : dict[str, dict[str, str]] = {}
    for tag in order:
        defaults[tag] = {}
        for name in seen[tag]:
            values = omitted[tag][name]
            if len(values) == 1:
                defaults[tag][name] = next(iter(values))
    return defaults


@checked
def readXmlDefaults(xr : QXmlStreamReader) -> dict[str, dict[str, str]]:
    """
    Reader is on the ``Defaults`` start element.
    Leaves the reader on that element's end token.
    """
    found : dict[str, dict[str, str]] = {}
    if xr.isEndElement():
        return found
    while not xr.atEnd():
        xr.readNext()
        if xr.isEndElement() and xr.name() == "Defaults":
            break
        if not xr.isStartElement():
            continue
        tag = str(xr.name())
        found[tag] = {
            underscore2space(str(xml_attr.name())) : str(xml_attr.value())
            for xml_attr in xr.attributes()
        }
        if xr.isEndElement():
            continue
        while not xr.atEnd():
            xr.readNext()
            if xr.isEndElement() and xr.name() == tag:
                break
    return found


@checked
def writeXmlDefaults(
    xw       : QXmlStreamWriter,
    defaults : dict[str, dict[str, str]],
) -> None:
    toXmlStartElement(xw, "Defaults")
    for tag, attrs in defaults.items():
        xw.writeStartElement(tag)
        for name, text in attrs.items():
            xw.writeAttribute(space2underscore(name), text)
        xw.writeEndElement()
    toXmlEndElement(xw)


def _setXmlProperty(prop : Property, raw : str) -> None:
    kind  = prop.kind()
    value : Any = raw
    if kind not in (DataKind.STR, DataKind.TEXT):
        value = str2val(raw, kind.types()[0].__name__)
    prop.setValue(value)


def _writeWorthyProperties(
    obj : PropertiesMixin,
    xw  : QXmlStreamWriter,
) -> None:
    for name, prop in obj.properties.items():
        if not prop.worthy():
            continue
        xw.writeAttribute(
            space2underscore(name),
            val2str(prop.value(raw=True)),
        )


def _writeDefaultedProperties(
    obj      : PropertiesMixin,
    xw       : QXmlStreamWriter,
    defaults : dict[str, str],
) -> None:
    for name, prop in obj.properties.items():
        text = val2str(prop.value(raw=True))
        if name not in _ALWAYS_WRITTEN \
        and name in defaults \
        and defaults[name] == text:
            continue
        xw.writeAttribute(space2underscore(name), text)


@checked
def toXmlProperties(obj : PropertiesMixin, xw : QXmlStreamWriter) -> None:
    state = _xml_defaults.get()
    tag   = _xmlTag(obj)
    if state is None or tag is None:
        _writeWorthyProperties(obj, xw)
        return
    _writeDefaultedProperties(obj, xw, state.by_tag.get(tag, {}))


def _applyXmlDefaults(
    obj   : PropertiesMixin,
    state : XmlDefaults,
    attrs : dict[str, str],
) -> None:
    tag = _xmlTag(obj)
    if tag is None:
        return
    defaults = state.by_tag.get(tag, {})
    for name, prop in obj.properties.items():
        if not prop.isInherent():
            continue
        if name in defaults:
            code = val2str(prop.value(raw=True))
            key  = (tag, name)
            if defaults[name] != code and key not in state.warned:
                state.warned.add(key)
                logger().warning(
                    f"{tag} default {name}={defaults[name]!r} "
                    f"disagrees with {code!r}"
                )
        elif name not in attrs:
            logger().warning(
                f"{tag} omits {name}, which has no default"
            )
    for name, text in defaults.items():
        if name in attrs or name not in obj.properties:
            continue
        prop = obj.properties[name]
        if val2str(prop.value(raw=True)) == text:
            continue
        _setXmlProperty(prop, text)


@checked
def fromXmlProperties(obj : PropertiesMixin, xr : QXmlStreamReader) -> None:
    attrs = {
        underscore2space(str(xml_attr.name())) : str(xml_attr.value())
        for xml_attr in xr.attributes()
    }
    state = _xml_defaults.get()
    if state is not None:
        _applyXmlDefaults(obj, state, attrs)
    for name, raw in attrs.items():
        if name in obj.properties:
            _setXmlProperty(obj.properties[name], raw)
        else:
            obj.propertyAdd(name, DataKind.STR, raw)
    xr.readNext()
