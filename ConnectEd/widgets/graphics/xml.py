# XML support functions for graphics scenes and items

from PyQt6.QtCore    import QPointF, QByteArray, QMimeData, \
                            QXmlStreamReader, QXmlStreamWriter
from PyQt6.QtWidgets import QApplication, QGraphicsItem

from ...app import logger

from ...core.check import checked
from ...core.defs  import MIME_TYPE
from ...core.utils import underscore2space, val2str

from .properties import PropertiesMixin


def toXmlBegin(name : str, xw : QXmlStreamWriter) -> None:
    xw.writeStartElement(name)

def toXmlProperties(instance : "PropertiesMixin", xw : QXmlStreamWriter) -> None:
    for name in instance.properties.names():
        if not instance.properties.worthy(name):
            continue
        value = instance.properties.value(name)
        xw.writeAttribute(underscore2space(name), val2str(value))

def toXmlEnd(xw : QXmlStreamWriter) -> None:
    xw.writeEndElement()

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
    if pos is None:
        pos = QPointF(0, 0)
    buffer = QByteArray()
    xw = QXmlStreamWriter(buffer)
    toXmlBegin(xw)
    xw.writeStartElement("Metadata")
    if pos is not None:
        xw.writeAttribute("pos", val2str(pos))
    xw.writeEndElement()
    for instance in items:
        instance.toXml(xw)
    toXmlEnd(xw)
    mime_data = QMimeData()
    mime_data.setData(MIME_TYPE, buffer)
    clipboard = QApplication.clipboard()
    clipboard.setMimeData(mime_data)

@checked
def paste() -> tuple[list["PropertiesMixin"], QPointF | None]:
    clipboard = QApplication.clipboard()
    mime_data = clipboard.mimeData()
    if mime_data and mime_data.hasFormat(MIME_TYPE):
        buffer = mime_data.data(MIME_TYPE)
        if buffer:
            xr = QXmlStreamReader(buffer)
            try:
                return fromXmlItems(xr)
            except ValueError as e:
                logger().error(f"paste error: {e}")
                if xr.hasError():
                    logger().error(f"XML parser error: {xr.errorString()} at line {xr.lineNumber()}, column {xr.columnNumber()}")
            except Exception as e:
                logger().error(f"Unexpected error during paste: {str(e)}")
                import traceback
                traceback.print_exc()
    return [], None
