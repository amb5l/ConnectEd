__all__ = [
    'DrawingItem', 'SymbolItem', 'DiagramItem',
    'DbItem', 'DesignItem', 'LibraryItem',
    'Model'
]

from typing  import Optional

from PyQt6.QtCore import Qt, QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtGui  import QStandardItemModel, QStandardItem

from . import logger, \
              LIB_EXT, DSN_EXT, \
              copy as master_copy, paste as master_paste, \
              fromXmlBegin, open, saveBegin, saveEnd, val2str, str2val

from ..widgets import DrawingScene, DiagramScene, SymbolScene

from .. import hub

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..widgets import DrawingScene, SymbolScene, DiagramScene


class DrawingItem(QStandardItem):
    SCENE_CLASS = DrawingScene

    scene : DrawingScene

    def __init__(self, scene : Optional[DrawingScene] = None) -> None:
        self.scene = scene if scene else self.SCENE_CLASS()
        super().__init__(self.scene.name)
        self.setData(self.scene, Qt.ItemDataRole.UserRole)
        self.setFlags(self.flags() | Qt.ItemFlag.ItemIsEditable)

    copy = master_copy

    def toXml(self, xw : QXmlStreamWriter) -> None:
        self.scene.toXml(xw)

    @classmethod
    def fromXml(cls, xr : QXmlStreamReader) -> 'DesignItem':
        cls_name = cls.__name__.replace('Item', '')
        if xr.name() != cls_name:
            raise ValueError(f'Expected {cls_name} element, got {xr.name()}')
        scene = cls.SCENE_CLASS.fromXml(xr)
        drawing_item : DrawingItem = cls(scene)
        drawing_item.setText(scene.name)
        return drawing_item

class SymbolItem(DrawingItem):
    SCENE_CLASS = SymbolScene

    scene : SymbolScene

class DiagramItem(DrawingItem):
    SCENE_CLASS = DiagramScene

    scene : DiagramScene

class DbItem(QStandardItem):
    XML_ATTRIBUTES = {}
    XML_PROPERTIES = {
        'name' : ('str', QStandardItem.setText, QStandardItem.text)
    }

    path : Optional[str]

    def __init__(self) -> None:
        u = 'Untitled' + self.__class__.__name__.replace('Item', '')
        super().__init__(hub.name_counter.get(u))
        self.setFlags(self.flags() | Qt.ItemFlag.ItemIsEditable)
        self.path = None

    @classmethod
    def fromXmlBegin(cls, xr : QXmlStreamReader) -> 'DbItem':
        fromXmlBegin(xr, cls.__name__.replace('Item', ''))
        db_item = cls()
        attributes = xr.attributes()
        for attribute in attributes:
            attr_name = attribute.name()
            attr_value_str = attribute.value()
            if attr_name in DesignItem.XML_ATTRIBUTES:
                attr_type_name = DesignItem.XML_ATTRIBUTES[attr_name]
                setattr(
                    db_item, attr_name,
                    str2val(attr_value_str, attr_type_name)
                )
            elif attr_name in DesignItem.XML_PROPERTIES:
                type_name, setter, _ = DesignItem.XML_PROPERTIES[attr_name]
                setter(db_item, str2val(attr_value_str, type_name))
            else:
                logger.warning(f'Unexpected attribute: {attr_name} value: {attr_value_str}')
        xr.readNext()
        return db_item

    def fromXmlEnd(self, xr : QXmlStreamReader) -> None:
        while not (xr.isEndElement() and xr.name() == self.__class__.__name__.replace('Item', '')):
            xr.readNext()

    def toXmlBegin(self, xw : QXmlStreamWriter) -> None:
        xw.writeStartElement(self.__class__.__name__.replace('Item', ''))
        for name, _ in self.XML_ATTRIBUTES.items():
            value = getattr(self, name)
            xw.writeAttribute(name, val2str(value))
        for name, (_, _, getter) in self.XML_PROPERTIES.items():
            value = getter(self)
            xw.writeAttribute(name, val2str(value))

    def toXmlEnd(self, xw : QXmlStreamWriter) -> None:
        xw.writeEndElement()

    @classmethod
    def load(cls, file : str) -> 'DbItem':
        with open(file, 'r') as f:
            data = f.read()
            xr = QXmlStreamReader(data)
            return cls.fromXml(xr)

    def save(self, path : Optional[str] = None) -> None:
        if path is not None:
            self.path = path
        if self.path is None:
            self.path = self.saveAs()
        else:
            xw, file = saveBegin(self.path)
            self.toXml(xw)
            saveEnd(xw, file)

    copy = master_copy

class LibraryItem(DbItem):
    FILE_EXT = LIB_EXT

    def toXml(self : 'LibraryItem', xw : QXmlStreamWriter) -> None:
        self.toXmlBegin(xw)
        for i in range(self.rowCount()):
            symbol_item : SymbolItem = self.child(i)
            symbol_scene = symbol_item.scene
            symbol_scene.toXml(xw)
        self.toXmlEnd(xw)

    @classmethod
    def fromXml(cls, xr : QXmlStreamReader) -> 'LibraryItem':
        db_item = cls.fromXmlBegin(xr)
        while not (xr.isEndElement() and xr.name() == cls.__name__.replace('Item', '')):
            xr.readNext()
        return db_item

class DesignItem(DbItem):
    FILE_EXT = DSN_EXT

    diagrams : QStandardItem
    symbols  : QStandardItem

    def __init__(self : 'DesignItem') -> None:
        super().__init__()
        self.diagrams = QStandardItem('Diagrams')
        self.diagrams.setEditable(False)
        font = self.diagrams.font() # TODO use settings
        font.setItalic(True)
        self.diagrams.setFont(font)
        self.appendRow(self.diagrams)
        self.symbols = QStandardItem('Symbol Cache')
        self.symbols.setEditable(False)
        font = self.symbols.font() # TODO use settings
        font.setItalic(True)
        self.symbols.setFont(font)
        self.appendRow(self.symbols)

    @classmethod
    def fromXml(cls, xr : QXmlStreamReader) -> 'DesignItem':
        db_item = cls.fromXmlBegin(xr)
        while not (xr.isEndElement() and xr.name() == cls.__name__.replace('Item', '')):
            if xr.tokenType() == QXmlStreamReader.TokenType.StartElement:
                if xr.name() == 'Diagrams':
                    xr.readNext()  # Move past <Diagrams>
                    while not (xr.isEndElement() and xr.name() == 'Diagrams'):
                        if xr.tokenType() == QXmlStreamReader.TokenType.StartElement:
                            if xr.name() == 'Diagram':
                                diagram_item = DiagramItem.fromXml(xr)
                                db_item.diagrams.appendRow(diagram_item)
                            else:
                                raise ValueError(f"Unexpected element in Diagrams: {xr.name()}")
                        xr.readNext()
                elif xr.name() == 'SymbolCache':
                    xr.readNext()  # Move past <SymbolCache>
                    while not (xr.isEndElement() and xr.name() == 'SymbolCache'):
                        if xr.tokenType() == QXmlStreamReader.TokenType.StartElement:
                            if xr.name() == 'Symbol':
                                symbol_item = SymbolItem.fromXml(xr)
                                db_item.symbols.appendRow(symbol_item)
                            else:
                                raise ValueError(f"Unexpected element in SymbolCache: {xr.name()}")
                        xr.readNext()
                else:
                    raise ValueError(f"Unexpected element in Design: {xr.name()}")
            xr.readNext()
        db_item.fromXmlEnd(xr)
        return db_item

    def toXml(self : 'DesignItem', xw : QXmlStreamWriter) -> None:
        self.toXmlBegin(xw)
        xw.writeStartElement('Diagrams')
        for i in range(self.diagrams.rowCount()):
            diagram_item : DiagramItem = self.diagrams.child(i)
            diagram_scene = diagram_item.scene
            diagram_scene.toXml(xw)
        xw.writeEndElement()
        xw.writeStartElement('SymbolCache')
        for i in range(self.symbols.rowCount()):
            symbol_item : SymbolItem = self.symbols.child(i)
            symbol_scene = symbol_item.scene
            symbol_scene.toXml(xw)
        self.toXmlEnd(xw)

class Model(QStandardItemModel):
    designs   : QStandardItem
    libraries : QStandardItem

    def __init__(self) -> None:
        super().__init__()
        self.setHorizontalHeaderLabels(['Database Hierarchy'])
        self.designs = QStandardItem('Designs')
        self.designs.setEditable(False)
        font = self.designs.font()
        font.setBold(True)
        self.designs.setFont(font)
        self.appendRow(self.designs)
        self.libraries = QStandardItem('Libraries')
        self.libraries.setEditable(False)
        font = self.libraries.font()
        font.setBold(True)
        self.libraries.setFont(font)
        self.appendRow(self.libraries)

    def newDesign(self : 'Model') -> DesignItem:
        item = DesignItem()
        self.designs.appendRow(item)
        return item

    def newLibrary(self : 'Model') -> LibraryItem:
        item = LibraryItem()
        self.libraries.appendRow(item)
        return item

    def newDiagram(
        self   : 'Model',
        parent : QStandardItem
    ) -> DiagramItem | None:
        item = None
        if self.getItemDescription(parent) == 'Design':
            parent = parent.diagrams
        if self.getItemDescription(parent) == 'Diagrams':
            item = DiagramItem()
            parent.appendRow(item)
        else:
            logger.warning(
                f'Unexpected parent item: {parent.text()} ({type(parent)})'
            )
        return item

    def newSymbol(
        self   : 'Model',
        parent : QStandardItem
    ) -> SymbolItem | None:
        item = None
        if self.getItemDescription(parent) == 'Symbol Cache' \
        or self.getItemDescription(parent) == 'Library':
            item = SymbolItem()
            parent.appendRow(item)
        else:
            logger.warning(
                f'Unexpected parent item: {parent.text()} ({type(parent)})'
            )
        return item

    def load(self : 'Model', path : str) -> DbItem:
        db_item = None
        if path.endswith(DSN_EXT):
            db_item = DesignItem.load(path)
            self.designs.appendRow(db_item)
        elif path.endswith(LIB_EXT):
            db_item = LibraryItem.load(path)
            self.libraries.appendRow(db_item)
        else:
            logger.warning(f'Unsupported file extension: {path}')
        return db_item

    def close(self : 'Model', item: QStandardItem) -> None:
        """Close a database and remove it from the model."""
        if isinstance(item, DesignItem):
            for i in range(self.designs.rowCount()):
                if item == self.designs.child(i):
                    self.designs.removeRow(i)
        elif isinstance(item, LibraryItem):
            for i in range(self.libraries.rowCount()):
                if item == self.libraries.child(i):
                    self.libraries.removeRow(i)
        else:
            logger.warning(f'Unsupported item: {item.text()} ({type(item)})')

    def copy(self : 'Model', item : QStandardItem) -> None:
        master_copy(item)

    def paste(self : 'Model', item : QStandardItem) -> None:
        paste_items = master_paste()
        if paste_items:
            match self.getItemDescription(item):
                case 'Designs':
                    valid_item_type_names = ['DesignItem']
                case 'Libraries':
                    valid_item_type_names = ['LibraryItem']
                case 'Diagrams':
                    valid_item_type_names = ['DiagramItem']
                case 'Symbol Cache':
                    valid_item_type_names = ['SymbolItem']
                case 'Libraries':
                    valid_item_type_names = ['SymbolItem']
                case _:
                    raise ValueError(
                        f'Cannot paste into item: {item.text()} ({type(item)})')
            invalid_item_type_names = []
            invalid_item_count = 0
            for paste_item in paste_items:
                paste_item_type_name = type(paste_item).__name__
                if paste_item_type_name not in valid_item_type_names:
                    invalid_item_type_names.append(paste_item_type_name)
                    invalid_item_count += 1
                else:
                    item.appendRow(paste_item)
                    # TODO: handle duplicate names
            if invalid_item_count:
                # TODO message box
                n = invalid_item_count
                s = ', '.join(invalid_item_type_names)
                raise ValueError(f'{n} invalid items for paste operation: {s}')

    def getDbItemFromScene(self : 'Model', scene : 'DrawingScene') -> 'DbItem':
        for i in range(self.designs.rowCount()):
            db_item = self.designs.child(i)
            for j in range(db_item.diagrams.rowCount()):
                drawing_item : DrawingItem = db_item.diagrams.child(j)
                if scene == drawing_item.scene:
                    return db_item
            for j in range(db_item.symbols.rowCount()):
                drawing_item : DrawingItem = db_item.symbols.child(j)
                if scene == drawing_item.scene:
                    return db_item
        for i in range(self.libraries.rowCount()):
            db_item = self.libraries.child(i)
            for j in range(db_item.rowCount()):
                drawing_item : DrawingItem = db_item.child(j)
                if scene == drawing_item.scene:
                    return db_item
        return None

    def getItemDescription(self : 'Model', i : QStandardItem) -> str | None:
        if i.text() == 'Designs':
            if type(i).__name__ == 'QStandardItem':
                return 'Designs'
            raise ValueError(f'Expected QStandardItem: {i.text()} ({type(i)})')
        elif i.text() == 'Libraries':
            if type(i).__name__ == 'QStandardItem':
                return 'Libraries'
            raise ValueError(f'Expected QStandardItem: {i.text()} ({type(i)})')
        elif i.parent().text() == 'Designs':
            if type(i).__name__ == 'DesignItem':
                return 'Design'
            s = f'Expected DesignItem: {i.text()} ({type(i)})'
            raise ValueError(s)
        elif i.parent().text() == 'Libraries':
            if isinstance(i, LibraryItem):
                return 'Library'
            s = f'Expected LibraryItem: {i.text()} ({type(i)})'
            raise ValueError(s)
        elif i.text() == 'Diagrams':
            if type(i).__name__ == 'QStandardItem':
                return 'Diagrams'
            raise ValueError(f'Expected QStandardItem: {i.text()} ({type(i)})')
        elif i.text() == 'Symbol Cache':
            if type(i).__name__ == 'QStandardItem':
                return 'Symbol Cache'
            raise ValueError(f'Expected QStandardItem: {i.text()} ({type(i)})')
        elif i.parent().text() == 'Diagrams':
            if isinstance(i, DiagramItem):
                return 'Diagram'
            s = f'Expected DiagramItem: {i.text()} ({type(i)})'
            raise ValueError(s)
        elif i.parent().text() == 'Symbol Cache':
            if isinstance(i, SymbolItem):
                return 'Design Symbol'
            s = f'Expected SymbolItem (Symbol Cache): {i.text()} type: ({type(i)})'
            raise ValueError(s)
        elif i.parent().text() == 'Libraries':
            if isinstance(i, SymbolItem):
                return 'Library Symbol'
            s = f'Expected SymbolItem: {i.text()} type: ({type(i)})'
            raise ValueError(s)
        raise ValueError(f'Unsupported item: {i.text()}  type: {type(i)}')
