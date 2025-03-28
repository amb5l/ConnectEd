__all__ = [
    'DrawingItem', 'SymbolItem', 'DiagramItem',
    'DbItem', 'DesignItem', 'LibraryItem',
    'DbModel'
]

from typing  import Optional
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui  import QStandardItemModel, QStandardItem

from ..core import LIB_EXT, DSN_EXT

from .. import hub

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..widgets import DrawingScene


class DrawingItem(QStandardItem):
    SCENE_TYPE : str

    scene : 'DrawingScene'

    def __init__(self : 'DrawingItem', name : Optional[str] = None) -> None:
        if name is None:
            u = 'Untitled' + self.__class__.__name__.replace('Item', '')
            name = hub.name_counter.get(u)
        super().__init__(name)
        # Import the scene type here to avoid circular import
        from ..widgets import DrawingScene, SymbolScene, DiagramScene
        # Get the appropriate scene class based on SCENE_TYPE string
        if self.SCENE_TYPE == 'DrawingScene':
            scene_class = DrawingScene
        elif self.SCENE_TYPE == 'SymbolScene':
            scene_class = SymbolScene
        elif self.SCENE_TYPE == 'DiagramScene':
            scene_class = DiagramScene
        else:
            raise ValueError(f"Unknown scene type: {self.SCENE_TYPE}")
        self.scene = scene_class()
        self.setData(self.scene, Qt.ItemDataRole.UserRole)

class SymbolItem(DrawingItem):
    SCENE_TYPE = 'SymbolScene'

class DiagramItem(DrawingItem):
    SCENE_TYPE = 'DiagramScene'

class DbItem(QStandardItem):
    path    : str
    symbols : QStandardItem

    def __init__(self : 'DbItem', path : Optional[str] = None) -> None:
        if path is None:
            u = 'Untitled' + self.__class__.__name__.replace('Item', '')
            path = hub.name_counter.get(u) + self.FILE_EXT
        self.path = path
        name = Path(path).stem
        super().__init__(name)
        self.symbols = self

    def setPath(self : 'DbItem', path: str) -> None:
        self.path = path
        name = Path(path).stem
        self.setText(name)

    def save(self : 'DbItem') -> None:
        print('TODO: save database')

class LibraryItem(DbItem):
    FILE_EXT = LIB_EXT

class DesignItem(DbItem):
    FILE_EXT = DSN_EXT

    diagrams : QStandardItem

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

    def new_design(self : 'DbModel') -> None:
        design_item = DesignItem()
        diagram_item = DiagramItem()
        design_item.diagrams.appendRow(diagram_item)
        self.designs.appendRow(design_item)
        if hub.main_window and hub.main_window.db_explorer:
            db_explorer = hub.main_window.db_explorer.db_explorer
            db_explorer.expand(self.indexFromItem(design_item))
            db_explorer.expand(self.indexFromItem(design_item.diagrams))
            db_explorer.edit_diagram(diagram_item)

    def new_library(self : 'DbModel') -> None:
        self.libraries.appendRow(LibraryItem())

    def edit_diagram(self : 'DbModel', item : DiagramItem) -> None:
        from ..widgets import DiagramScene, DiagramView, DiagramSubWindow
        design_item : DesignItem = item.parent().parent()
        diagram_name = item.text()
        diagram_scene : DiagramScene = item.data(Qt.ItemDataRole.UserRole)
        subwindow = DiagramSubWindow()
        diagram_view = DiagramView(diagram_scene)
        subwindow.setWidget(diagram_view)
        subwindow.setWindowTitle(f'{design_item.text()}: {diagram_name}')
        hub.main_window.mdi_area.addSubWindow(subwindow)
        subwindow.showMaximized()
        hub.main_window.menu_bar.updateWindowMenu()

    def close(self, db_item: 'DbItem') -> None:
        """Close a database and remove it from the model."""
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

    def get_db_from_scene(self : 'DbModel', scene : 'DrawingScene') -> 'DbItem':
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
