from __future__ import annotations

from typing          import Self
from collections.abc import Iterable

from PyQt6.QtCore import QTransposeProxyModel, QObject
from PyQt6.QtGui  import QStandardItemModel

from ...app import logger

from ...core.check import checked


class TableModel(QStandardItemModel):
    """Table model with horizontal header group labels support."""

    _hgroups : list[str] | None

    def __init__(self : Self, parent : QObject | None = None) -> None:
        self._hgroups = None
        super().__init__(parent)

    @checked
    def setHorizontalHeaderLabels(
        self   : Self,
        labels : Iterable[str | None]
    ) -> None:
        super().setHorizontalHeaderLabels(labels)
        self._hgroups = None

    @checked
    def setHorizontalHeaderGroupLabels(
        self   : Self,
        labels : Iterable[tuple[str, str]]
    ) -> None:
        pairs = list(labels)
        if self.columnCount() not in (0, len(pairs)):
            logger().error(
                f"Header group labels length ({len(pairs)}) "
                f"!= columnCount ({self.columnCount()})"
            )
        self._hgroups = [group for group, _label in pairs]
        super().setHorizontalHeaderLabels([label for _group, label in pairs])

    def horizontalHeaderGroupLabels(self : Self) -> list[str] | None:
        return None if self._hgroups is None else list(self._hgroups)


class TableProxy(QTransposeProxyModel):
    pass
