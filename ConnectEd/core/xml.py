__all__ = [
    "fromXmlBegin",
    "saveBegin",
    "saveEnd",
    "save",
    "loadItems",
    "copy",
    "paste",
    "toXmlBegin",
    "toXmlEnd",
    "toXmlAttrs",
    "fromXmlAttrs",
    "fromXmlItems"
]

from typing import TypeAlias, Union, Any, Optional

from PyQt6.QtCore    import QByteArray, QXmlStreamWriter, QXmlStreamReader, \
                            QFile, QIODevice, QMimeData, QPointF
from PyQt6.QtWidgets import QApplication

from . import logger, APP_NAME, MIME_TYPE, val2str, str2val

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .db import DesignDbItem, LibraryDbItem, DiagramItem, SymbolItem
    from ..widgets import ElementMixin


XmlItemTypes: TypeAlias = Union[
    "DesignDbItem",
    "LibraryDbItem",
    "DiagramItem",
    "SymbolItem",
    "ElementMixin"
]

def toXmlBegin(xw : QXmlStreamWriter) -> None:
    xw.setAutoFormatting(True)
    xw.setAutoFormattingIndent(2)
    xw.writeStartDocument()
    xw.writeStartElement(APP_NAME) # TODO: version

def toXmlAttrs(instance : Any, xw : QXmlStreamWriter) -> None:
    for name, value in instance.getPropertyNamesAndValues().items():
        xml_attr_name = name.replace(" ", "_")
        xw.writeAttribute(xml_attr_name, value)

def toXmlEnd(xw : QXmlStreamWriter) -> None:
    xw.writeEndDocument()

def fromXmlBegin(xr : QXmlStreamReader, element_name : str) -> None:
    xr.readNext()
    while not (xr.isStartElement() and xr.name() == element_name):
        xr.readNext()

def fromXmlEnd(xr : QXmlStreamReader, element_name : str) -> None:
    while not (xr.isEndElement() and xr.name() == element_name):
        xr.readNext()

def fromXmlAttrs(instance : Any, xr : QXmlStreamReader) -> None:
    attributes = xr.attributes()
    for attribute in attributes:
        xml_attr_name = attribute.name()
        value = attribute.value()
        property_name = xml_attr_name.replace("_", " ")
        instance.setPropertyValue(property_name, value)
    xr.readNext()

def fromXmlItems(
    xr : QXmlStreamReader
) -> tuple[list[XmlItemTypes], Optional[QPointF]]:
    from .db import DesignDbItem, LibraryDbItem, DiagramItem, SymbolItem
    from ..widgets import element_class_dict
    pos = None
    items = []
    fromXmlBegin(xr, APP_NAME)
    xr.readNext()
    while not (xr.isEndElement() and xr.name() == APP_NAME):
        if xr.tokenType() == QXmlStreamReader.TokenType.StartElement:
            if xr.name() == "Metadata":
                attributes = xr.attributes()
                for attr in attributes:
                    if attr.name() == "pos":
                        pos = str2val(attr.value(), "QPointF")
                xr.readNext()
                while not (xr.isEndElement() and xr.name() == "Metadata"):
                    xr.readNext()
            else:
                match xr.name():
                    case "DesignDbItem":
                        item = DesignDbItem.fromXml(xr)
                    case "LibraryDbItem":
                        item = LibraryDbItem.fromXml(xr)
                    case "DiagramItem":
                        item = DiagramItem.fromXml(xr)
                    case "SymbolItem":
                        item = SymbolItem.fromXml(xr)
                    case _:  # Assume it's an Element
                        if xr.name() in element_class_dict:
                            item_class = element_class_dict[xr.name()]
                            item = item_class.fromXml(xr)
                        else:
                            item = None
                            logger.warning(f"Unexpected element: {xr.name()}")
                if item:
                    items.append(item)
        xr.readNext()
    return items, pos

def saveBegin(path : str) -> tuple[QXmlStreamWriter, QFile]:
    # TODO: handle file open error
    file = QFile(path)
    if file.open(QIODevice.OpenModeFlag.WriteOnly | QIODevice.OpenModeFlag.Text):
        xw = QXmlStreamWriter(file)
        toXmlBegin(xw)
        return xw, file

def saveEnd(xw : QXmlStreamWriter, file : QFile) -> None:
    xw.writeEndElement() # ConnectEd
    toXmlEnd(xw)
    file.close()

def save(instance : Any, path : str) -> None:
    xw, file = saveBegin(path)
    instance.toXml(xw)
    saveEnd(xw, file)

def loadItems(path : str) -> list[XmlItemTypes]:
    # TODO: handle file open error
    file = QFile(path)
    if file.open(QIODevice.OpenModeFlag.ReadOnly | QIODevice.OpenModeFlag.Text):
        xr = QXmlStreamReader(file)
        r = fromXmlItems(xr)
        file.close()
    else:
        r = []
    return r

def copy(instances : Any | list[Any], pos : QPointF = QPointF(0, 0)) -> None:
    if not isinstance(instances, list):
        instances = [instances]
    buffer = QByteArray()
    xw = QXmlStreamWriter(buffer)
    toXmlBegin(xw)
    xw.writeStartElement("Metadata")
    if pos is not None:
        xw.writeAttribute("pos", val2str(pos))
    xw.writeEndElement()
    for instance in instances:
        instance.toXml(xw)
    toXmlEnd(xw)
    mime_data = QMimeData()
    mime_data.setData(MIME_TYPE, buffer)
    clipboard = QApplication.clipboard()
    clipboard.setMimeData(mime_data)

def paste() -> tuple[list[XmlItemTypes], Optional[QPointF]]:
    clipboard = QApplication.clipboard()
    mime_data = clipboard.mimeData()
    if mime_data and mime_data.hasFormat(MIME_TYPE):
        buffer = mime_data.data(MIME_TYPE)
        if buffer:
            xr = QXmlStreamReader(buffer)
            try:
                return fromXmlItems(xr)
            except ValueError as e:
                logger.error(f"paste error: {e}")
                if xr.hasError():
                    logger.error(f"XML parser error: {xr.errorString()} at line {xr.lineNumber()}, column {xr.columnNumber()}")
            except Exception as e:
                logger.error(f"Unexpected error during paste: {str(e)}")
                import traceback
                traceback.print_exc()
    logger.warning("No valid ConnectEd data in clipboard")
    return [], None
