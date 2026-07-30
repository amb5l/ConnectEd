from typing import Self

from PyQt6.QtCore    import QRectF
from PyQt6.QtGui     import QPainter

from ....app import settings

from ....core.check import checked

from ....widgets.graphics.items.symbol import SymbolDefinitionItem

from .diagram import DiagramScene


class SymbolScene(DiagramScene):
    """Scene for editing a single symbol definition."""

    # instance attributes
    _item : SymbolDefinitionItem | None  # definition being edited

    @checked
    def __init__(
        self : Self,
        item : SymbolDefinitionItem | None = None
    ) -> None:
        super().__init__()
        self._item = item
        if item is not None:
            self.addItem(item)

    def item(self : Self) -> SymbolDefinitionItem | None:
        return self._item

    def setItem(self : Self, item : SymbolDefinitionItem | None) -> None:
        self._item = item
        self.clear()
        if item is not None:
            self.addItem(item)

    def drawBackground(
        self    : Self,
        painter : QPainter | None,
        rect    : QRectF | None
    ) -> None:
        if painter is None or rect is None:
            return
        # background
        painter.fillRect(rect, settings().get("theme/background"))
