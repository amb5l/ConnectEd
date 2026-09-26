from __future__ import annotations

import weakref

from typing import Self

from PyQt6.QtCore import QRectF
from PyQt6.QtGui  import QPainter

from ....app                           import settings

from ....core.check                    import checked

from ....widgets.graphics.items.symbol import \
    SymbolDefinitionItem, SymbolInstanceItem

from .diagram                          import DiagramScene


class SymbolScene(DiagramScene):
    """Scene for editing a single symbol definition."""

    # instance attributes
    _definition : SymbolDefinitionItem | None
    _instance   : weakref.ref[SymbolInstanceItem] | None

    @checked
    def __init__(
        self       : Self,
        definition : SymbolDefinitionItem | None = None,
        instance   : SymbolInstanceItem   | None = None,
    ) -> None:
        super().__init__()
        self._definition = None
        self._instance = None
        self.setSymbol(definition)
        self.setInstance(instance)

    @checked
    def symbol(self : Self) -> SymbolDefinitionItem | None:
        return self._definition

    @checked
    def setSymbol(
        self       : Self,
        definition : SymbolDefinitionItem | None,
    ) -> None:
        self._definition = definition
        self.clear()
        if definition is not None:
            self.addItem(definition)

    @checked
    def instance(self : Self) -> SymbolInstanceItem | None:
        if self._instance is None:
            return None
        return self._instance()

    @checked
    def setInstance(
        self     : Self,
        instance : SymbolInstanceItem | None,
    ) -> None:
        self._instance = None if instance is None else weakref.ref(instance)

    def drawBackground(
        self    : Self,
        painter : QPainter | None,
        rect    : QRectF   | None
    ) -> None:
        if painter is None or rect is None:
            return
        # background
        painter.fillRect(rect, settings().get("theme/background"))
