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
    from .model    import DesignDb, LibraryDb, Diagram, Symbol
    from ..widgets import ElementMixin


XmlItemTypes: TypeAlias = Union[
    "DesignDb",
    "LibraryDb",
    "Diagram",
    "Symbol",
    "ElementMixin"
]

def toXmlBegin(xw : QXmlStreamWriter) -> None:
    xw.setAutoFormatting(True)
    xw.setAutoFormattingIndent(2)
    xw.writeStartDocument()
    xw.writeStartElement(APP_NAME) # TODO: version

def toXmlAttrs(instance : Any, xw : QXmlStreamWriter) -> None:
    attrs = instance.XML_ATTRS
    for attr_name, attr_info in attrs.items():
        if isinstance(attr_info, str):
            if hasattr(instance, attr_name):
                value = getattr(instance, attr_name)
                xw.writeAttribute(attr_name, val2str(value))
        elif isinstance(attr_info, tuple):
            _, always, _, getter = attr_info
            if always or hasattr(instance, attr_name):
                value = getter(instance)
                xw.writeAttribute(attr_name, val2str(value))
        else:
            logger.warning(f"Unexpected XML attribute info: {attr_info}")

def toXmlEnd(xw : QXmlStreamWriter) -> None:
    xw.writeEndDocument()

def fromXmlBegin(xr : QXmlStreamReader, token_name : str) -> None:
    while not xr.atEnd() and \
        xr.tokenType() != QXmlStreamReader.TokenType.StartElement:
        xr.readNext()
    if xr.atEnd():
        raise ValueError("Empty or invalid XML")
    if xr.name() != token_name:
        raise ValueError(f"Expected '{token_name}' element, got '{xr.name()}'")

def fromXmlAttrs(instance : Any, xr : QXmlStreamReader) -> None:
    attributes = xr.attributes()
    for attribute in attributes:
        attr_name = attribute.name()
        attr_value_str = attribute.value()
        if attr_name in instance.XML_ATTRS:
            attr_info = instance.XML_ATTRS[attr_name]
            if isinstance(attr_info, str):
                setattr(
                    instance, attr_name,
                    str2val(attr_value_str, attr_info)
                )
            elif isinstance(attr_info, tuple):
                type_name, _, setter, _ = attr_info
                setter(instance, str2val(attr_value_str, type_name))
            else:
                logger.warning(f"Unexpected XML attribute info: {attr_info}")
        else:
            logger.warning(f"Unexpected attribute: {attr_name} value: {attr_value_str}")
    xr.readNext()

def fromXmlItems(
    xr : QXmlStreamReader
) -> tuple[list[XmlItemTypes], Optional[QPointF]]:
    from .model    import DesignDb, LibraryDb, Diagram, Symbol
    from ..widgets import element_class_dict
    copy_pos = None
    items = []
    fromXmlBegin(xr, APP_NAME)
    xr.readNext()
    while not (xr.isEndElement() and xr.name() == APP_NAME):
        if xr.tokenType() == QXmlStreamReader.TokenType.StartElement:
            if xr.name() == "Metadata":
                attributes = xr.attributes()
                for attr in attributes:
                    if attr.name() == "pos":
                        copy_pos = str2val(attr.value(), "QPointF")
                xr.readNext()
                while not (xr.isEndElement() and xr.name() == "Metadata"):
                    xr.readNext()
            else:
                match xr.name():
                    case "DesignDb":
                        item = DesignDb.fromXml(xr)
                    case "LibraryDb":
                        item = LibraryDb.fromXml(xr)
                    case "Diagram":
                        item = Diagram.fromXml(xr)
                    case "Symbol":
                        item = Symbol.fromXml(xr)
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
    return items, copy_pos

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
    from ..widgets.drawing.items import ElementMixin
    clipboard = QApplication.clipboard()
    mime_data = clipboard.mimeData()
    if mime_data and mime_data.hasFormat(MIME_TYPE):
        buffer = mime_data.data(MIME_TYPE)
        if buffer:
            xr = QXmlStreamReader(buffer)
            try:
                return fromXmlItems(xr)
            except ValueError as e:
                print(f"paste error: {e}")
                if xr.hasError():
                    print(f"XML parser error: {xr.errorString()} at line {xr.lineNumber()}, column {xr.columnNumber()}")
            except Exception as e:
                print(f"Unexpected error during paste: {str(e)}")
                import traceback
                traceback.print_exc()
    logger.warning("No valid ConnectEd data in clipboard")
    return [], None
