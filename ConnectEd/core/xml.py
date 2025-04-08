__all__ = ['saveBegin', 'saveEnd', 'open', 'copy', 'paste']

from typing import Any, Union, TypeAlias

from PyQt6.QtCore    import QByteArray, QXmlStreamWriter, QXmlStreamReader, \
                            QFile, QIODevice
from PyQt6.QtWidgets import QApplication

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .db import DesignItem, LibraryItem, DiagramItem, SymbolItem
    from ..widgets.elements import Element
    from ..widgets.scenes   import DiagramScene, SymbolScene


XmlItemTypes: TypeAlias = Union[
    'DesignItem',
    'LibraryItem',
    'DiagramItem',
    'SymbolItem',
    'Element'
]

def toXmlBegin(xw : QXmlStreamWriter) -> None:
    xw.setAutoFormatting(True)
    xw.setAutoFormattingIndent(2)
    xw.writeStartDocument()
    xw.writeStartElement('ConnectEd') # TODO: version

def toXmlEnd(xw : QXmlStreamWriter) -> None:
    xw.writeEndDocument()

def fromXml(xr : QXmlStreamReader) -> list[XmlItemTypes]:
    from .db import DesignItem, LibraryItem, DiagramItem, SymbolItem
    from ..widgets.elements import element_class_dict
    while not xr.atEnd() and xr.tokenType() != QXmlStreamReader.TokenType.StartElement:
        xr.readNext()
    if xr.atEnd():
        raise ValueError("Empty or invalid XML")
    if xr.name() != 'ConnectEd':
        raise ValueError(f"Expected 'ConnectEd' root element, got '{xr.name()}'")
    xr.readNext()
    result = []
    while not (xr.isEndElement() and xr.name() == 'ConnectEd'):
        if xr.tokenType() == QXmlStreamReader.TokenType.StartElement:
            match xr.name():
                case 'Design':
                    design_item = DesignItem.fromXml(xr)
                    result.append(design_item)
                case 'Library':
                    library_item = LibraryItem.fromXml(xr)
                    result.append(library_item)
                case 'Diagram':
                    diagram_item = DiagramItem.fromXml(xr)
                    result.append(diagram_item)
                case 'Symbol':
                    symbol_item = SymbolItem.fromXml(xr)
                    result.append(symbol_item)
                case _: # assume it's an Element
                    if xr.name() in element_class_dict:
                        element_class = element_class_dict[xr.name()]
                        element = element_class.fromXml(xr)
                        result.append(element)
                    else:
                        raise ValueError(f"Unexpected element: {xr.name()}")
        if xr.isEndElement() and xr.name() == 'ConnectEd':
            break
        xr.readNext()
    return result

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

def open(path : str) -> list[XmlItemTypes]:
    # TODO: handle file open error
    file = QFile(path)
    if file.open(QIODevice.OpenModeFlag.ReadOnly | QIODevice.OpenModeFlag.Text):
        xr = QXmlStreamReader(file)
        r = fromXml(xr)
        file.close()
    else:
        r = []
    return r

def copy(instance : Any) -> None:
    buffer = QByteArray()
    xw = QXmlStreamWriter(buffer)
    toXmlBegin(xw)
    instance.toXml(xw)
    toXmlEnd(xw)
    clipboard = QApplication.clipboard()
    clipboard.setText(buffer.data().decode('utf-8'))

def paste() -> list[XmlItemTypes]:
    clipboard = QApplication.clipboard()
    buffer = clipboard.text()
    if buffer:
        xr = QXmlStreamReader(buffer)
        try:
            items = fromXml(xr)
            return items
        except ValueError as e:
            print(f'paste error: {e}')
            if xr.hasError():
                print(f'XML parser error: {xr.errorString()} at line {xr.lineNumber()}, column {xr.columnNumber()}')
        except Exception as e:
            print(f'Unexpected error during paste: {str(e)}')
            import traceback
            traceback.print_exc()
    return []
