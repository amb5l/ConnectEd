__all__ = [
    'DrawingItem', 'SymbolItem', 'DiagramItem',
    'DbItem', 'DesignItem', 'LibraryItem',
    'DbModel'
]

from typing  import Optional
from pathlib import Path

from PyQt6.QtCore    import Qt, QXmlStreamWriter
from PyQt6.QtWidgets import QDialog
from PyQt6.QtGui     import QStandardItemModel, QStandardItem

from ..core    import LIB_EXT, DSN_EXT, copy as master_copy, \
                      saveBegin, saveEnd
from ..widgets import FileSaveAsDialog

from .. import hub

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..widgets import DrawingScene, SymbolScene, DiagramScene


class DrawingItem(QStandardItem):
    SCENE_TYPE : str

    scene : 'DrawingScene'

    def __init__(
        self  : 'DrawingItem',
        scene : Optional['DrawingScene'] = None
    ) -> None:
        from ..widgets import SymbolScene, DiagramScene
        if self.SCENE_TYPE == 'DrawingScene':
            scene_class = DrawingScene
        elif self.SCENE_TYPE == 'SymbolScene':
            scene_class = SymbolScene
        elif self.SCENE_TYPE == 'DiagramScene':
            scene_class = DiagramScene
        else:
            raise ValueError(f"Unknown scene type: {self.SCENE_TYPE}")
        self.scene = scene if scene else scene_class()
        super().__init__(self.scene.name)
        self.setData(self.scene, Qt.ItemDataRole.UserRole)

    copy = master_copy

    def toXml(self : 'DrawingItem', xw : QXmlStreamWriter) -> None:
        self.scene.toXml(xw)

class SymbolItem(DrawingItem):
    SCENE_TYPE = 'SymbolScene'

    scene : 'SymbolScene'

class DiagramItem(DrawingItem):
    SCENE_TYPE = 'DiagramScene'

    scene : 'DiagramScene'

class DbItem(QStandardItem):
    path    : str

    def __init__(self : 'DbItem', path : Optional[str] = None) -> None:
        if path is None:
            u = 'Untitled' + self.__class__.__name__.replace('Item', '')
            path = hub.name_counter.get(u) + self.FILE_EXT
        self.path = path
        name = Path(path).stem
        super().__init__(name)

    def setPath(self : 'DbItem', path: str) -> None:
        self.path = path
        name = Path(path).stem
        self.setText(name)

    def save(self : 'DesignItem') -> None:
        if Path(self.path).parent == Path('.'):
            self.saveAs()
        else:
            xw, file = saveBegin(self.path)
            self.toXml(xw)
            saveEnd(xw, file)

    def saveAs(self : 'DesignItem') -> None:
        dialog = FileSaveAsDialog(
            hub.main_window,
            self.__class__.__name__.replace('Item', '')
        )
        result = dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            selected_files = dialog.selectedFiles()
            if selected_files:
                new_path = selected_files[0]
                print(f'Saving as: {new_path}')
                self.setPath(new_path)
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

    def __init__(self : 'DesignItem', path : Optional[str] = None) -> None:
        super().__init__(path)
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
        if item.text() == 'Designs':
            design_item = DesignItem()
            diagram_item = DiagramItem()
            design_item.diagrams.appendRow(diagram_item)
            item.appendRow(design_item)
            if hub.main_window and hub.main_window.db_explorer:
                db_explorer = hub.main_window.db_explorer.db_explorer
                db_explorer.expand(self.indexFromItem(design_item))
                db_explorer.expand(self.indexFromItem(design_item.diagrams))
                db_explorer.editDrawing(diagram_item)
        elif item.text() == 'Libraries':
            library_item = LibraryItem()
            item.appendRow(library_item)
            if hub.main_window and hub.main_window.db_explorer:
                db_explorer = hub.main_window.db_explorer.db_explorer
                db_explorer.expand(self.indexFromItem(library_item))
        elif item.text() == 'Diagrams':
            item.appendRow(DiagramItem())
            if hub.main_window and hub.main_window.db_explorer:
                db_explorer = hub.main_window.db_explorer.db_explorer
                db_explorer.expand(self.indexFromItem(item))
        elif item.parent().text() == 'Libraries':
            item.appendRow(SymbolItem())
        else:
            raise ValueError(f"Bad item: {item} {item.text()} {type(item)}")

    def editDrawing(self : 'DbModel', item : DrawingItem) -> None:
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
            raise ValueError(f"Unknown drawing scene: {type(drawing_scene)}")
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
            raise ValueError(f"Unknown scene: {type(scene)}")

    def saveAsScene(self : 'DbModel', scene : 'DrawingScene') -> None:
        db_item = self.getDbItemFromScene(scene)
        if db_item:
            db_item.saveAs()
        else:
            raise ValueError(f"Unknown scene: {type(scene)}")

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
            raise ValueError(f"Unknown database item type: {type(db_item)}")

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
