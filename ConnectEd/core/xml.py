from typing import Self, Protocol, Any, cast, runtime_checkable
from collections.abc import Callable

from PyQt6.QtCore    import QXmlStreamWriter, QXmlStreamReader, \
                            QFile, QIODevice, QByteArray, QMimeData
from PyQt6.QtWidgets import QApplication

from ..app import logger

from .check import checked
from .defs  import APP_NAME, MIME_TYPE
from .utils import cleanPath


XmlHandler = Callable[[QXmlStreamReader], Any]


class XmlProtocol(Protocol):
    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        ...

    @classmethod
    def fromXml(cls : type[Self], xr : QXmlStreamReader) -> Self:
        ...


@runtime_checkable
class FileXmlProtocol(XmlProtocol, Protocol):
    def path(self : Self) -> str:
        ...

    def setPath(self : Self, path : str) -> None:
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


def saveXml(
    instance : FileXmlProtocol,
    path     : str | None = None,
) -> str | None:
    if path is None:
        save_path = instance.path()
    else:
        save_path = cleanPath(path)
    if save_path == "":
        logger().warning(f"Document has no path to save to: {instance}")
        return None
    temp_path = f"{save_path}.tmp"
    temp_file = QFile(temp_path)
    if not temp_file.open(
        QIODevice.OpenModeFlag.WriteOnly | QIODevice.OpenModeFlag.Text
    ):
        logger().warning(f"Failed to open file {temp_path} for writing")
        return None
    try:
        xw = QXmlStreamWriter(temp_file)
        xw.setAutoFormatting(True)
        xw.setAutoFormattingIndent(2)
        xw.writeStartDocument()
        toXmlStartElement(xw, APP_NAME)
        instance.toXml(xw)
        toXmlEndElement(xw)
        xw.writeEndDocument()
    except Exception as e:
        logger().error(f"Failed to save {save_path}: {e}")
        temp_file.close()
        temp_file.remove()
        return None
    temp_file.close()
    if QFile.exists(save_path) and not QFile.remove(save_path):
        logger().warning(f"Failed to replace {save_path}")
        temp_file.remove()
        return None
    if not QFile.rename(temp_path, save_path):
        logger().warning(f"Failed to rename {temp_path} to {save_path}")
        temp_file.remove()
        return None
    return save_path


def loadXml(
    path     : str,
    elements : dict[str, type],
) -> FileXmlProtocol | None:
    """
    Load the first document element under ``<ConnectEd>`` from *path*.

    *elements* maps XML tag names to document classes (``fromXml`` handlers).
    Returns the loaded instance with ``setPath`` applied, or ``None`` on failure.

    Note: ``elements`` values are typed as ``type`` at runtime so typeguard accepts
    concrete ``Doc`` subclasses; static callers should pass ``type[FileXmlProtocol]``.
    """
    path = cleanPath(path)
    file = QFile(path)
    flag_enum = QIODevice.OpenModeFlag
    if not file.exists():
        logger().warning(f"{path} not found")
        return None
    if not file.open(flag_enum.ReadOnly | flag_enum.Text):
        logger().warning(f"Failed to open file {path} for reading")
        return None
    if file.size() == 0:
        logger().error(f"File is empty: {path}")
        return None
    xr = QXmlStreamReader(file)
    try:
        while not xr.atEnd():
            if xr.isStartElement() and xr.name() == APP_NAME:
                break
            xr.readNext()
        else:
            logger().error(f"No {APP_NAME} root element in {path}")
            return None
        while not xr.atEnd():
            xr.readNext()
            if xr.isEndElement() and xr.name() == APP_NAME:
                logger().error(f"No document element in {path}")
                return None
            if not xr.isStartElement():
                continue
            tag = xr.name()
            doc_cls = elements.get(tag)
            if doc_cls is None:
                logger().error(f"Unknown document tag {tag!r} in {path}")
                return None
            try:
                doc = cast(FileXmlProtocol, doc_cls.fromXml(xr))
            except Exception:
                logger().exception(f"Failed to load {path}")
                return None
            doc.setPath(path)
            return doc
    finally:
        file.close()
    return None


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
    if clipboard is not None:
        clipboard.setMimeData(mime_data)


@checked
def pasteXml(
    xref : dict[str, type[XmlProtocol]]
) -> tuple[list[XmlProtocol], dict[str, str]]:
    """
    Builds objects from clipboard XML; returns them and envelope metadata.
    """
    clipboard = QApplication.clipboard()
    if clipboard is None:
        return [], {}
    buffer = clipboard.text()
    xr = QXmlStreamReader(buffer)
    items, attributes = fromXmlWrapper(xr, "Clipboard", xref)
    return items, attributes


def clipboardHasData() -> bool:
    """
    Checks if the clipboard has data in the expected format.
    """

    clipboard = QApplication.clipboard()
    if clipboard is None:
        return False
    mime_data = clipboard.mimeData()
    return mime_data is not None and mime_data.hasFormat(MIME_TYPE)
