__all__ = [
    'DrawingItem', 'SymbolItem', 'DiagramItem',
    'DbItem', 'DesignItem', 'LibraryItem',
    'DbModel'
]

from typing  import Optional, Union

from PyQt6.QtCore    import Qt, QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtWidgets import QDialog
from PyQt6.QtGui     import QStandardItemModel, QStandardItem

from ..core    import LIB_EXT, DSN_EXT, \
                      copy as master_copy, \
                      paste as master_paste, \
                      saveBegin, saveEnd
from ..widgets import FileSaveAsDialog

from ..widgets.elements import element_class_dict

from .. import hub

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..widgets import DrawingScene, SymbolScene, DiagramScene


class DrawingItem(QStandardItem):
    from ..widgets import DrawingScene, SymbolScene, DiagramScene
    SCENE_CLASS : Union[DrawingScene, SymbolScene, DiagramScene] = DrawingScene

    scene : DrawingScene

    def __init__(self, scene : Optional[DrawingScene] = None) -> None:
        self.scene = scene if scene else self.SCENE_CLASS()
        super().__init__(self.scene.name)
        self.setData(self.scene, Qt.ItemDataRole.UserRole)

    copy = master_copy

    def toXml(self, xw : QXmlStreamWriter) -> None:
        self.scene.toXml(xw)

    @classmethod
    def fromXml(cls, xr : QXmlStreamReader) -> 'DesignItem':
        cls_name = cls.__name__.replace('Item', '')
        if xr.name() != cls_name:
            raise ValueError(f'Expected {cls_name} element, got {xr.name()}')
        name = xr.attributes().value('name')
        drawing_item : DrawingItem = cls(name)
        while not (xr.isEndElement() and xr.name() == cls_name):
            xr.readNext()
            name = xr.name()
            if name in element_class_dict:
                cls = element_class_dict[name]
                element = cls.fromXml(xr)
                drawing_item.scene.addItem(element)
                xr.readNext()
            else:
                raise ValueError(f"Unexpected element: {name}")
        return drawing_item

class SymbolItem(DrawingItem):
    from ..widgets import SymbolScene
    SCENE_CLASS = SymbolScene

    scene : SymbolScene

class   DiagramItem(DrawingItem):
    from ..widgets import DiagramScene
    SCENE_CLASS = DiagramScene

    scene : DiagramScene

class DbItem(QStandardItem):
    name : str
    path : Optional[str]

    def __init__(self) -> None:
        u = 'Untitled' + self.__class__.__name__.replace('Item', '')
        self.name = hub.name_counter.get(u)
        self.path = None
        super().__init__(self.name)

    def setName(self, name: str) -> None:
        self.name = name
        self.setText(name)

    def save(self) -> None:
        if self.path is None:
            self.saveAs()
        else:
            xw, file = saveBegin(self.path)
            self.toXml(xw)
            saveEnd(xw, file)

    def saveAs(self) -> None:
        dialog = FileSaveAsDialog(
            hub.main_window,
            self.__class__.__name__.replace('Item', '')
        )
        result = dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            selected_files = dialog.selectedFiles()
            if selected_files:
                new_path = selected_files[0]
                self.setName(new_path)
                self.save()

    copy = master_copy

class LibraryItem(DbItem):
    FILE_EXT = LIB_EXT

    def toXml(self : 'LibraryItem', xw : QXmlStreamWriter) -> None:
        xw.writeStartElement('Library')
        xw.writeAttribute('path', self.text())
        for i in range(self.rowCount()):
            symbol_item : SymbolItem = self.child(i)
            symbol_scene = symbol_item.scene
            symbol_scene.toXml(xw)
        xw.writeEndElement()

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

    def toXml(self : 'DesignItem', xw : QXmlStreamWriter) -> None:
        xw.writeStartElement('Design')
        xw.writeAttribute('path', self.text())
        xw.writeStartElement('Diagrams')
        for i in range(self.diagrams.rowCount()):
            diagram_item : DiagramItem = self.diagrams.child(i)
            diagram_scene = diagram_item.scene
            diagram_scene.toXml(xw)
        xw.writeEndElement()
        xw.writeStartElement('Symbol Cache')
        for i in range(self.symbols.rowCount()):
            symbol_item : SymbolItem = self.symbols.child(i)
            symbol_scene = symbol_item.scene
            symbol_scene.toXml(xw)
        xw.writeEndElement()

    @classmethod
    def fromXml(cls : 'DesignItem', xr : QXmlStreamReader) -> 'DesignItem':
        if xr.name() != 'Design':
            raise ValueError(f"Expected Design element, got {xr.name()}")
        name = xr.attributes().value('name')
        design_item : DesignItem = cls(name)
        while not (xr.isEndElement() and xr.name() == 'Design'):
            match xr.name():
                case 'Diagrams':
                    xr.readNext()
                    while not (xr.isEndElement() and xr.name() == 'Diagrams'):
                        diagram_item = DiagramItem.fromXml(xr)
                        design_item.diagrams.appendRow(diagram_item)
                case 'Symbol Cache':
                    xr.readNext()
                    while not (xr.isEndElement() and xr.name() == 'Symbol Cache'):
                        symbol_item = SymbolItem.fromXml(xr)
                        design_item.symbols.appendRow(symbol_item)
                case _:
                    raise ValueError(f"Unexpected element: {xr.name()}")
        return design_item

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

    def newItem(self : 'DbModel', item : QStandardItem) -> None:
        match self.getItemTypeStr(item):
            case 'Designs':
                design_item = DesignItem()
                diagram_item = DiagramItem()
                design_item.diagrams.appendRow(diagram_item)
                item.appendRow(design_item)
                if hub.main_window and hub.main_window.db_explorer:
                    db_explorer = hub.main_window.db_explorer.db_explorer
                    db_explorer.expand(self.indexFromItem(design_item))
                    db_explorer.expand(self.indexFromItem(design_item.diagrams))
                    db_explorer.editDrawing(diagram_item)
            case 'Libraries':
                library_item = LibraryItem()
                item.appendRow(library_item)
                if hub.main_window and hub.main_window.db_explorer:
                    db_explorer = hub.main_window.db_explorer.db_explorer
                    db_explorer.expand(self.indexFromItem(library_item))
            case 'Diagrams':
                item.appendRow(DiagramItem())
                if hub.main_window and hub.main_window.db_explorer:
                    db_explorer = hub.main_window.db_explorer.db_explorer
                    db_explorer.expand(self.indexFromItem(item))
            case 'Symbol Cache':
                item.appendRow(SymbolItem())
            case _:
                raise ValueError(f'Bad item: {item} {item.text()} {type(item)}')

    def editDrawing(self : 'DbModel', item : DrawingItem) -> None:
        if not isinstance(item, DiagramItem):
            raise ValueError(f'Expected DiagramItem:{item.text()} ({type(item)})')
        """Edit the drawing, focusing the first existing subwindow if available."""
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

    def newWindow(self : 'DbModel', item : DrawingItem) -> None:
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

    def saveDb(self : 'DbModel', db_item: 'DbItem') -> None:
        db_item.save()

    def saveAsDb(self : 'DbModel', db_item: 'DbItem') -> None:
        db_item.saveAs()

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

    def closeDb(self : 'DbModel', db_item: 'DbItem') -> None:
        """Close a database and remove it from the model."""
        # TODO offer to save if modified
        if isinstance(db_item, DesignItem):
            for i in range(self.designs.rowCount()):
                if db_item == self.designs.child(i):
                    self.designs.removeRow(i)
        elif isinstance(db_item, LibraryItem):
            for i in range(self.libraries.rowCount()):
                if db_item == self.libraries.child(i):
                    self.libraries.removeRow(i)
        else:
            raise ValueError(f'Unknown database item type: {type(db_item)}')

    def copy(self : 'DbModel', item : QStandardItem) -> None:
        master_copy(item)

    def paste(self : 'DbModel', item : QStandardItem) -> None:
        paste_items = master_paste()
        print('paste_items', paste_items)
        if paste_items:
            match self.getItemTypeStr(item):
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
                    # handle duplicate names
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

    def getItemTypeStr(self : 'DbModel', i : QStandardItem) -> str | None:
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
