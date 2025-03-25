__all__ = ['Database', 'Library', 'Design', 'DatabaseManager']

from typing import Optional, Type, List

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..widgets.scenes import SymbolScene, DiagramScene


class Database:
    path    : Optional[str] = None
    symbols : list['SymbolScene']

    def __init__(
        self : 'Design',
        path : Optional[str] = None
    ) -> None:
        self.path    = path
        self.symbols = []

    def new_symbol(self) -> 'SymbolScene':
        from ..widgets.scenes import SymbolScene
        symbol = SymbolScene()
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
        path : Optional[str] = None
    ) -> None:
        super().__init__(path)
        self.diagrams = []

    def new_diagram(self) -> 'DiagramScene':
        from ..widgets.scenes import DiagramScene
        diagram = DiagramScene()
        self.diagrams.append(diagram)
        return diagram

class DatabaseManager:
    ALLOWED_TYPES: List[Type[Database]] = [Library, Design]

    databases : list[Database]

    def __init__(self) -> None:
        self.databases = []

    def new(
        self    : 'DatabaseManager',
        db_type : Type[Database]
    ) -> Database:
        if db_type not in self.ALLOWED_TYPES:
            raise ValueError(f"Database type {db_type.__name__} is not allowed")
        db = db_type()
        self.databases.append(db)
        return db

    def open(
        self : 'DatabaseManager',
        path : str
    ) -> Database:
        print('TODO: open database')
