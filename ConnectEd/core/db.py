__all__ = [
    'DrawingItem', 'SymbolItem', 'DiagramItem',
    'DbItem', 'DesignItem', 'LibraryItem',
    'DbModel'
]

from typing  import Optional

from PyQt6.QtCore    import Qt, QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtWidgets import QDialog
from PyQt6.QtGui     import QStandardItemModel, QStandardItem

from ..core    import logger, \
                      LIB_EXT, DSN_EXT, \
                      copy as master_copy, paste as master_paste, \
                      fromXmlBegin, open, saveBegin, saveEnd, val2str, str2val
from ..widgets import DrawingScene, DiagramScene, SymbolScene, \
                      FileOpenDialog, FileSaveAsDialog

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
    XML_PROPERTIES = { 'name' : ('str', QStandardItem.setText, QStandardItem.text) }

    name : str
    path : Optional[str]

    def __init__(self) -> None:
        u = 'Untitled' + self.__class__.__name__.replace('Item', '')
        self.name = hub.name_counter.get(u)
        self.path = None
        super().__init__(self.name)
        self.setFlags(self.flags() | Qt.ItemFlag.ItemIsEditable)
    def setName(self, name: str) -> None:
        self.name = name
        self.setText(name)

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

    @classmethod
    def fromXmlFile(cls, file : str) -> 'DbItem':
        with open(file, 'r') as f:
            data = f.read()
            xr = QXmlStreamReader(data)
            return cls.fromXml(xr)

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

    def save(self) -> None:
        if self.path is None:
            self.path = self.saveAs()
        else:
            xw, file = saveBegin(self.path)
            self.toXml(xw)
            saveEnd(xw, file)

    def saveAs(self) -> str:
        dialog = FileSaveAsDialog(
            hub.main_window,
            self.__class__.__name__.replace('Item', '')
        )
        result = dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            selected_files = dialog.selectedFiles()
            path = selected_files[0]
            if path:
                self.path = path
                self.save()
                self.setName(path)
                return path

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

class DbModel(QStandardItemModel):
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
        self.itemChanged.connect(self.changeItem)

    def newItem(self : 'DbModel', item : QStandardItem) -> None:
        explorer = hub.main_window.explorer.explorer \
            if hub.main_window and hub.main_window.explorer else None
        match self.getItemTypeName(item):
            case 'Designs':
                design_item = DesignItem()
                diagram_item = DiagramItem()
                design_item.diagrams.appendRow(diagram_item)
                item.appendRow(design_item)
                if explorer:
                    explorer.expand(self.indexFromItem(design_item))
                    explorer.expand(self.indexFromItem(design_item.diagrams))
                    explorer.editItem(diagram_item)
            case 'Libraries':
                library_item = LibraryItem()
                item.appendRow(library_item)
                if explorer:
                    explorer.expand(self.indexFromItem(library_item))
            case 'Diagrams':
                item.appendRow(DiagramItem())
                if explorer:
                    explorer.expand(self.indexFromItem(item))
            case 'Symbol Cache':
                item.appendRow(SymbolItem())
            case _:
                raise ValueError(f'Bad item: {item} {item.text()} {type(item)}')

    def openItem(self : 'DbModel', item : QStandardItem) -> None:
        match item.text():
            case 'Designs':
                type_name = 'Design'
            case 'Libraries':
                type_name = 'Library'
            case _:
                raise ValueError(f'Unknown item: {item.text()}')
        self.open(type_name)

    def open(self : 'DbModel', type_name : Optional[str] = None) -> None:
        explorer = hub.main_window.explorer.explorer \
            if hub.main_window and hub.main_window.explorer else None
        dialog = FileOpenDialog(hub.main_window, type_name)
        result = dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            files = dialog.selectedFiles()
            for file in files:
                opened_items = open(file)
                for opened_item in opened_items:
                    match type(opened_item).__name__:
                        case 'DesignItem':
                            self.designs.appendRow(opened_item)
                            if explorer:
                                explorer.expand(self.indexFromItem(opened_item))
                                explorer.expand(self.indexFromItem(opened_item.diagrams))
                                if opened_item.diagrams.rowCount() > 0:
                                    explorer.editItem(opened_item.diagrams.child(0))
                        case 'LibraryItem':
                            self.libraries.appendRow(opened_item)
                        case _:
                            raise ValueError(f'Unsupported item type: {opened_item.text()} ({type(opened_item).__name__})')

    def editItem(self : 'DbModel', item : QStandardItem) -> None:
        """Edit the drawing, focusing the first existing subwindow if available."""
        if isinstance(item, DrawingItem):
            from ..widgets import DrawingScene, DrawingView, DrawingSubWindow, \
                                  SymbolScene, SymbolView, SymbolSubWindow, \
                                  DiagramScene, DiagramView, DiagramSubWindow
            for subwindow in hub.main_window.mdi_area.subWindowList():
                if not isinstance(subwindow, DrawingSubWindow):
                    continue
                if not isinstance(subwindow.widget(), DrawingView):
                    continue
                if not isinstance(subwindow.widget().scene(), DrawingScene):
                    continue
                if item.scene != subwindow.widget().scene():
                    continue
                hub.main_window.mdi_area.setActiveSubWindow(subwindow)
                subwindow.show()
                subwindow.raise_()
                subwindow.setFocus()
                return
            drawing_name = item.text()
            drawing_scene : DrawingScene = item.data(Qt.ItemDataRole.UserRole)
            if isinstance(drawing_scene, DiagramScene):
                drawing_view = DiagramView(drawing_scene)
                db_item = item.parent().parent()
                subwindow = DiagramSubWindow(hub.main_window.mdi_area)
            elif isinstance(drawing_scene, SymbolScene):
                drawing_view = SymbolView(drawing_scene)
                db_item = item.parent()
                subwindow = SymbolSubWindow(hub.main_window.mdi_area)
            else:
                raise ValueError(f'Unknown drawing scene: {type(drawing_scene)}')
            subwindow.setWidget(drawing_view)
            subwindow.setWindowTitle(f'{db_item.text()}: {drawing_name}')
            hub.main_window.mdi_area.addSubWindow(subwindow)
            subwindow.showMaximized()
            hub.main_window.menu_bar.updateWindowMenu()
        else:
            logger.warning(f'Unsupported item: {item.text()} ({type(item)})')

    def newItemWindow(self : 'DbModel', item : QStandardItem) -> None:
        if isinstance(item, DrawingItem):
            from ..widgets import DiagramScene, DiagramView, DiagramSubWindow, \
                                  SymbolScene, SymbolView, SymbolSubWindow
            if isinstance(item, DiagramItem):
                db_item : DesignItem = item.parent().parent()
                drawing_name = item.text()
                drawing_scene : DiagramScene = item.data(Qt.ItemDataRole.UserRole)
                subwindow = DiagramSubWindow()
                drawing_view = DiagramView(drawing_scene)
                subwindow.setWidget(drawing_view)
            elif isinstance(item, SymbolItem):
                db_item : LibraryItem = item.parent()
                drawing_name = item.text()
                drawing_scene : SymbolScene = item.data(Qt.ItemDataRole.UserRole)
                subwindow = SymbolSubWindow()
                drawing_view = SymbolView(drawing_scene)
                subwindow.setWidget(drawing_view)
            subwindow.setWindowTitle(f'{db_item.text()}: {drawing_name}')
            hub.main_window.mdi_area.addSubWindow(subwindow)
            subwindow.showMaximized()
            hub.main_window.menu_bar.updateWindowMenu()
        else:
            logger.warning(f'Unsupported item: {item.text()} ({type(item)})')

    def saveItem(self : 'DbModel', item: QStandardItem) -> None:
        if isinstance(item, DbItem):
            item.save()
        else:
            logger.warning(f'Unsupported item: {item.text()} ({type(item)})')

    def saveAsItem(self : 'DbModel', item: QStandardItem) -> None:
        if isinstance(item, DbItem):
            item.saveAs()
        else:
            logger.warning(f'Unsupported item: {item.text()} ({type(item)})')

    def saveScene(self : 'DbModel', scene : 'DrawingScene') -> None:
        db_item = self.getDbItemFromScene(scene)
        if db_item:
            db_item.save()
        else:
            raise ValueError(f'Unknown scene: {type(scene)}')

    def saveAsScene(self : 'DbModel', scene : 'DrawingScene') -> None:
        db_item = self.getDbItemFromScene(scene)
        if db_item:
            db_item.saveAs()
        else:
            raise ValueError(f'Unknown scene: {type(scene)}')

    def closeItem(self : 'DbModel', item: QStandardItem) -> None:
        """Close a database and remove it from the model."""
        # TODO offer to save if modified
        if isinstance(item, DesignItem):
            for i in range(self.designs.rowCount()):
                if item == self.designs.child(i):
                    self.designs.removeRow(i)
        elif isinstance(item, LibraryItem):
            for i in range(self.libraries.rowCount()):
                if item == self.libraries.child(i):
                    self.libraries.removeRow(i)
        else:
            logger.warning(f'Unknown database item type: {type(item)}')

    def changeItem(self : 'DbModel', item : QStandardItem) -> None:
        """Handle changes to items in the model, such as renaming."""
        if item.parent() and item.parent().text() in ('Diagrams', 'Symbol Cache'):
            scene = item.data(Qt.ItemDataRole.UserRole)
            if scene:
                scene.name = item.text()
        hub.main_window.mdi_area.update()

    def copy(self : 'DbModel', item : QStandardItem) -> None:
        master_copy(item)

    def paste(self : 'DbModel', item : QStandardItem) -> None:
        paste_items = master_paste()
        if paste_items:
            match self.getItemTypeName(item):
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

    def getDbItemFromScene(self : 'DbModel', scene : 'DrawingScene') -> 'DbItem':
        for i in range(self.designs.rowCount()):
            db_item = self.designs.child(i)
            for j in range(db_item.diagrams.rowCount()):
                drawing_item : DrawingItem = db_item.diagrams.child(j)
                if scene == drawing_item.scene:
                    return db_item
        for i in range(self.libraries.rowCount()):
            db_item = self.libraries.child(i)
            for j in range(db_item.rowCount()):
                drawing_item : DrawingItem = db_item.child(j)
                if scene == drawing_item.scene:
                    return db_item
        return None

    def getItemTypeName(self : 'DbModel', i : QStandardItem) -> str | None:
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
        elif i.parent().text() == 'Symbol Cache' \
          or i.parent().text() == 'Libraries':
            if isinstance(i, SymbolItem):
                return 'Symbol'
            s = f'Expected SymbolItem: {i.text()} type: ({type(i)})'
            raise ValueError(s)
        raise ValueError(f'Unsupported item: {i.text()}  type: {type(i)}')
