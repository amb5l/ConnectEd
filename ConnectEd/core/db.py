__all__ = ['Database', 'Library', 'Design', 'database_manager']

from typing import Optional, Type, List

from . import TypedList
from ..widgets.scenes import SymbolScene, DiagramScene


class Database:
    path    : Optional[str] = None
    symbols : TypedList[SymbolScene]

    def __init__(
        self : 'Design',
        path : Optional[str] = None
    ) -> None:
        self.path    = path
        self.symbols = TypedList(SymbolScene)

    def save(self) -> None:
        if self.path is None:
            print('TODO: get save path from dialog, then save')
        else:
            print('TODO: save database to existing path')

class Library(Database):
    pass

class Design(Database):
    diagrams : TypedList[DiagramScene]

    def __init__(
        self : 'Design',
        path : Optional[str] = None
    ) -> None:
        super().__init__(path)
        self.diagrams = TypedList(DiagramScene)

class DatabaseManager:
    ALLOWED_TYPES: List[Type[Database]] = [Library, Design]

    databases : TypedList[Database]

    def __init__(self) -> None:
        self.databases = TypedList(Database)

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

database_manager = DatabaseManager()
