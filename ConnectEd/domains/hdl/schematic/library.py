from typing import Any, Self

from ....core.types import DataKind

from .symbols       import SymbolsMixin

class HdlSchematicLibrary(SymbolsMixin):
    _name              : str
    _property_defaults : dict[str, tuple[DataKind, Any]]

    def __init__(self : Self) -> None:
        self.initSymbols()
        self._name = "Untitled"
        self._property_defaults = {}

    def name(self : Self) -> str:
        return self._name

    def setName(self : Self, name: str) -> None:
        self._name = name

    def getPropertyDefaults(self : Self) -> dict[str, tuple[DataKind, Any]]:
        return dict(self._property_defaults)

