from typing import Self, Protocol, Any
from collections.abc import Callable

from PyQt6.QtCore    import QXmlStreamWriter, QXmlStreamReader, \
                            QFile, QIODevice, QByteArray, QMimeData
from PyQt6.QtWidgets import QApplication

from ..app import logger

from .check import checked
from .defs  import APP_NAME, MIME_TYPE
from .utils import cleanPath


XmlHandler = Callable[[QXmlStreamReader], Any]


class PathProtocol(Protocol):
    def path(self : Self) -> str:
        ...

    def setPath(self : Self, path : str) -> None:
        ...

class XmlProtocol(Protocol):
    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        ...

    @classmethod
    def fromXml(cls : type[Self], xr : QXmlStreamReader) -> Self:
        ...


def toXmlStartElement(
    xw         : QXmlStreamWriter,
    tag        : str,
    attributes : dict[str, str] | None = None
) -> None:
    xw.writeStartElement(tag)
    if attributes is not None:
        for name, value in attributes.items():
            xw.writeAttribute(name, value)


def toXmlEndElement(xw : QXmlStreamWriter) -> None:
    xw.writeEndElement()


def fromXml(
    xr   : QXmlStreamReader,
    xref : dict[str, XmlHandler | type[XmlProtocol]],  # tag : handler mapping
    path : str | None = None,                          # path of loaded file
    ptag : str | None = None,                          # parent tag
) -> list[Any]:
    output = []
    while not xr.atEnd():
        if ptag is not None and xr.isEndElement() and xr.name() == ptag:
            break
        if xr.isStartElement():
            tag = xr.name()
            handler = xref.get(tag)
            if handler is None:
                logger().warning(f"Unknown element: {tag}")
            else:
                obj = handler.fromXml(xr) if isinstance(handler, type) else handler(xr)
                if obj is not None:
                    if path and hasattr(obj, "setPath"):
                        obj.setPath(path)
                    output.append(obj)
        xr.readNext()
    return output


def fromXmlWrapper(
    xr   : QXmlStreamReader,
    tag  : str,
    xref : dict[str, XmlHandler | type[XmlProtocol]]
) -> tuple[list[Any], dict[str, str]]:
    if not xr.readNextStartElement() or xr.name() != tag:
        logger().warning(f"No {tag} element found")
        return [], {}
    attributes = {a.name(): a.value() for a in xr.attributes()}
    return fromXml(xr, xref), attributes


@checked
def saveXml(
    instance : PathProtocol | XmlProtocol,
    path     : str | None = None
) -> bool:
    if path is None:
        path = instance.path()
    else:
        path = cleanPath(path)
        instance.setPath(path)
    if path == "":
        logger().warning(f"Document has no path to save to: {instance}")
        return False
    file = QFile(path)
    if not file.open(
        QIODevice.OpenModeFlag.WriteOnly | QIODevice.OpenModeFlag.Text
    ):
        logger().warning(f"Failed to open file {path} for writing")
        return False
    xw = QXmlStreamWriter(file)
    xw.setAutoFormatting(True)
    xw.setAutoFormattingIndent(2)
    xw.writeStartDocument()
    toXmlStartElement(xw, APP_NAME)
    instance.toXml(xw)
    toXmlEndElement(xw)
    xw.writeEndDocument()
    file.close()
    return True


def loadXml(
    path     : str,
    elements : dict[str, type[XmlProtocol]]
) -> list[XmlProtocol]:
    """
    Loads children of the first <ConnectEd> element from the file.
    """
    file = QFile(path)
    flag_enum = QIODevice.OpenModeFlag
    if not file.open(flag_enum.ReadOnly | flag_enum.Text):
        logger().warning(f"Failed to open file {path} for reading")
        return False
    xr = QXmlStreamReader(file)
    if not xr.readNextStartElement() or xr.name() != APP_NAME:
        logger().warning(f"No {APP_NAME} root element in {path}")
        return False
    fromXml(xr, elements, path)


def copyXml(
    items    : XmlProtocol | list[XmlProtocol],
    metadata : dict[str, str] | None = None
) -> None:
    """
    Copies the XML representation of the objects to the clipboard,
    enveloped inside a "Clipboard" element with metadata attributes.
    """
    if not isinstance(items, list):
        items = [items]
    buffer = QByteArray()
    xw = QXmlStreamWriter(buffer)
    xw.setAutoFormatting(True)
    xw.setAutoFormattingIndent(2)
    toXmlStartElement(xw, "Clipboard", metadata)
    for item in items:
        item.toXml(xw)
    toXmlEndElement(xw)
    mime_data = QMimeData()
    mime_data.setData(MIME_TYPE, buffer)
    clipboard = QApplication.clipboard()
    clipboard.setMimeData(mime_data)


@checked
def pasteXml(
    xref : dict[str, type[XmlProtocol]]
) -> tuple[list[XmlProtocol], dict[str, str]]:
    """
    Builds objects from clipboard XML; returns them and envelope metadata.
    """
    buffer = QApplication.clipboard().text()
    xr = QXmlStreamReader(buffer)
    items, attributes = fromXmlWrapper(xr, "Clipboard", xref)
    return items, attributes


def clipboardHasData() -> bool:
    """
    Checks if the clipboard has data in the expected format.
    """
    mime_data = QApplication.clipboard().mimeData()
    return mime_data is not None and mime_data.hasFormat(MIME_TYPE)
