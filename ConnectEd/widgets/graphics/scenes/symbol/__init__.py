from typing import Self

from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui  import QPainter, QPen

from .....app import settings

from .....core.check import checked
from .....core.defs  import PITCH

from ..diagram import DiagramScene

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...items.symbol import SymbolDefinitionItem


class SymbolScene(DiagramScene):
    """Scene for editing a single symbol definition."""

    # instance attributes
    _symbol : SymbolDefinitionItem | None  # symbol being edited
    _brect  : QRectF | None                # bounding rect of all items

    @checked
    def __init__(
        self   : Self,
        symbol : SymbolDefinitionItem | None = None
    ) -> None:
        super().__init__()
        self._symbol = symbol
        if symbol is not None:
            self.addItem(symbol)
        self._brect = None
        self.onChange()
        self.changed.connect(self.onChange)

    def onChange(self : Self) -> None:
        # get bounding rect of all items
        rect = self.itemsBoundingRect()
        # expand size if too small
        rect.setWidth(min(rect.size().width(), PITCH))
        rect.setHeight(min(rect.size().height(), PITCH))
        # store result
        self._brect = rect

    def symbol(self : Self) -> SymbolDefinitionItem | None:
        return self._symbol

    def drawBackground(
        self    : Self,
        painter : QPainter | None,
        rect    : QRectF | None
    ) -> None:
        if painter is None or rect is None:
            return
        # background
        painter.fillRect(rect, settings().get("theme/background"))
