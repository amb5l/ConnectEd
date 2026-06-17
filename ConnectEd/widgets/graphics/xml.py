# XML support functions for graphics scenes and items

from PyQt6.QtCore    import QPointF, QXmlStreamReader, QXmlStreamWriter
from PyQt6.QtWidgets import QApplication

from ...core.check import checked
from ...core.defs  import MIME_TYPE
from ...core.utils import underscore2space, val2str
from ...core.xml   import copyXml, fromXml, fromXmlWrapper, pasteXml

from .properties import PropertiesMixin


def toXmlProperties(instance : "PropertiesMixin", xw : QXmlStreamWriter) -> None:
    for name in instance.properties.names():
        if not instance.properties.worthy(name):
            continue
        value = instance.properties.value(name)
        xw.writeAttribute(underscore2space(name), val2str(value))


@checked
def fromXmlProperties(
    instance : "PropertiesMixin",
    xr       : QXmlStreamReader
) -> None:
    for xml_attr in xr.attributes():
        instance.properties.init(
            underscore2space(xml_attr.name()), xml_attr.value()
        )

@checked
def copy(
    items : "PropertiesMixin | list[PropertiesMixin]",
    pos   : QPointF | None = None
) -> None:
    if not isinstance(items, list):
        items = [items]
    metadata = None
    if pos is not None:
        metadata = {"X" : val2str(pos.x()), "Y" : val2str(pos.y())}
    copyXml(items, metadata)


@checked
def paste(xref : dict[str, type[XmlProtocol]]) -> tuple[list["PropertiesMixin"], QPointF | None]:
    buffer = QApplication.clipboard().text()
    xr = QXmlStreamReader(buffer)
    items, attributes = fromXmlWrapper(xr, "Clipboard", xref)
    x = attributes.get("X", None)
    y = attributes.get("Y", None)
    pos = None if x is None or y is None else QPointF(float(x), float(y))
    return items, pos


def copyXml(
    items    : XmlProtocol | list[XmlProtocol],
    metadata : dict[str, str] | None = None
) -> None:
    """Copies the XML representation of the objects to the clipboard."""
    if not isinstance(items, list):
        items = [items]
    buffer = QByteArray()
    xw = QXmlStreamWriter(buffer)
    xw.setAutoFormatting(True)
    xw.setAutoFormattingIndent(2)
    toXmlBegin(xw, "Clipboard", metadata)
    for item in items:
        item.toXml(xw)
    toXmlEnd(xw)
    mime_data = QMimeData()
    mime_data.setData(MIME_TYPE, buffer)
    clipboard = QApplication.clipboard()
    clipboard.setMimeData(mime_data)


def pasteXml(
    xref : dict[str, type[XmlProtocol]]
) -> tuple[list[XmlProtocol], dict[str, str]]:
    """Converts the clipboard content to a list of objects."""
    buffer = QApplication.clipboard().text()
    xr = QXmlStreamReader(buffer)
    items, attributes = fromXmlWrapper(xr, "Clipboard", xref)

    if not xr.readNextStartElement() or xr.name() != "Clipboard":
        logger().warning(f"No Clipboard root element in clipboard")
        # get attributes into dict
        return ([], {})
    attributes = {a.name(): a.value() for a in xr.attributes()}
    return (fromXml(xr, xref), attributes)
