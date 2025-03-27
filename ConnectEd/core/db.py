__all__ = ['Database', 'Library', 'Design', 'DatabaseManager']

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem

from typing import Optional, Type, List

from .. import hub

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..widgets.scenes import SymbolScene, DiagramScene


class Database:
    path    : Optional[str]
    name    : str
    symbols : list['SymbolScene']

    def __init__(
        self : 'Design',
        path : Optional[str] = None,
        name : Optional[str] = None
    ) -> None:
        self.path    = path
        self.name    = name if name is not None else 'Untitled' + str(hub.count)
        self.symbols = []

    def new_symbol(self) -> 'SymbolScene':
        from ..widgets.scenes import SymbolScene
        symbol = SymbolScene(db=self)
        self.symbols.append(symbol)
        return symbol

    def save(self) -> None:
        if self.path is None:
            print('TODO: get save path from dialog, then save')
        else:
            print('TODO: save database to existing path')

class Library(Database):
    pass

class Design(Database):
    diagrams : list['DiagramScene']

    def __init__(
        self : 'Design',
        path : Optional[str] = None,
        name : Optional[str] = None
    ) -> None:
        super().__init__(path, name)
        self.diagrams = []
        self.new_diagram()

    def new_diagram(self : 'Design') -> 'DiagramScene':
        from ..widgets.scenes import DiagramScene
        diagram = DiagramScene(db=self)
        self.diagrams.append(diagram)
        return diagram

class DatabaseManager:
    ALLOWED_TYPES: List[Type[Database]] = [Design, Library]

    model     : QStandardItemModel
    designs   : QStandardItem
    libraries : QStandardItem

    def __init__(self) -> None:
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Database Hierarchy'])
        self.designs = QStandardItem('Designs')
        self.designs.setEditable(False)
        font = self.designs.font()
        font.setBold(True)
        self.designs.setFont(font)
        self.model.appendRow(self.designs)
        self.libraries = QStandardItem('Libraries')
        self.libraries.setEditable(False)
        font = self.libraries.font()
        font.setBold(True)
        self.libraries.setFont(font)
        self.model.appendRow(self.libraries)

    def new(
        self    : 'DatabaseManager',
        db_type : Type[Database]
    ) -> Database:
        if db_type not in self.ALLOWED_TYPES:
            raise ValueError(f'Database type {db_type.__name__} is not allowed')
        db = db_type()
        self._add_to_model(db)
        return db

    def open(
        self : 'DatabaseManager',
        path : str
    ) -> Database:
        print('TODO: open database')

    def get_model(self) -> QStandardItemModel:
        """Return the model for use in a QTreeView."""
        return self.model

    def _add_to_model(self, db: Database) -> None:
        if isinstance(db, Design):
            db_item = QStandardItem(db.name)
            db_item.setEditable(False)
            db_item.setData(db, Qt.ItemDataRole.UserRole)
            self.designs.appendRow(db_item)
            diagrams_item = QStandardItem('Diagrams')
            diagrams_item.setEditable(False)
            font = diagrams_item.font()
            font.setItalic(True)
            diagrams_item.setFont(font)
            db_item.appendRow(diagrams_item)
            symbols_item = QStandardItem('Symbol Cache')
            symbols_item.setEditable(False)
            font = symbols_item.font()
            font.setItalic(True)
            symbols_item.setFont(font)
            db_item.appendRow(symbols_item)
            for diagram in db.diagrams:
                diag_item = QStandardItem(diagram.name)
                diag_item.setEditable(False) # TODO allow this to be edited
                diag_item.setData(diagram, Qt.ItemDataRole.UserRole)
                diagrams_item.appendRow(diag_item)
            for symbol in db.symbols:
                symbol_item = QStandardItem(symbol.name)
                symbol_item.setEditable(False)
                symbol_item.setData(symbol, Qt.ItemDataRole.UserRole)
                symbols_item.appendRow(symbol_item)
        elif isinstance(db, Library):
            db_item = QStandardItem(db.name)
            db_item.setEditable(False)
            db_item.setData(db, Qt.ItemDataRole.UserRole)
            self.libraries.appendRow(db_item)
            for symbol in db.symbols:
                symbol_item = QStandardItem(symbol.name)
                symbol_item.setEditable(False)
                symbol_item.setData(symbol, Qt.ItemDataRole.UserRole)
                db_item.appendRow(symbol_item)
        tree_view = hub.main_window.db_explorer.widget()
        design_index = self.model.indexFromItem(db_item)
        tree_view.expand(design_index)
        if isinstance(db, Design):
            tree_view.expand(self.model.indexFromItem(diagrams_item))
            tree_view.expand(self.model.indexFromItem(symbols_item))
