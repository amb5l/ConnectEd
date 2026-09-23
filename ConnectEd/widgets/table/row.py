from __future__ import annotations

from .item import TableItem


class TableRow:
    """
    Dict-shaped list of TableItems.
    """

    _names : list[str]
    _cells : list[TableItem | None]

    def __init__(self, names : list[str]) -> None:
        self._names = names
        self._cells = [None] * len(names)

    def __setitem__(self, name : str, cell : TableItem | None) -> None:
        self._cells[self._names.index(name)] = cell

    def cells(self) -> list[TableItem | None]:
        return self._cells
