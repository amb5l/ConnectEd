from __future__ import annotations

from typing import Self

from .item import TableItem


class TableRow:
    """
    Dict-shaped list of TableItems.
    """

    _names : list[str]
    _cells : list[TableItem | None]

    def __init__(self : Self, names : list[str]) -> None:
        self._names = names
        self._cells = [None] * len(names)

    def __setitem__(self : Self, name : str, cell : TableItem | None) -> None:
        self._cells[self._names.index(name)] = cell

    def cells(self : Self) -> list[TableItem | None]:
        return self._cells
