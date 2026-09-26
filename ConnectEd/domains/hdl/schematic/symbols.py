from typing import Self

from ....widgets.graphics.items.symbol import SymbolDefinitionItem


class SymbolsMixin:
    """Definitions mixin for schematic diagram, design and library."""

    _symbols : dict[str, SymbolDefinitionItem]

    def initSymbols(self : Self) -> None:
        self._symbols = {}

    def getSymbols(self : Self) -> dict[str, SymbolDefinitionItem]:
        return self._symbols

    def getSymbol(self : Self, name: str) -> SymbolDefinitionItem | None:
        return None if name not in self._symbols \
            else self._symbols[name]

    def addSymbol(self : Self, definition: SymbolDefinitionItem) -> None:
        if definition.name() in self._symbols:
            raise ValueError(f"Definition {definition.name()} already exists")
        self._symbols[definition.name()] = definition

    def addSymbols(self : Self, symbols: list[SymbolDefinitionItem]) -> None:
        for symbol in symbols:
            self.addSymbol(symbol)

    def renSymbol(self : Self, symbol: SymbolDefinitionItem, name: str) -> None:
        if symbol.name() in self._symbols:
            raise ValueError(f"Symbol {symbol.name()} already exists")
        self._symbols[name] = symbol
        del self._symbols[symbol.name()]

