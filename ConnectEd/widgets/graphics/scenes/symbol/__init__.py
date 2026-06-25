from typing import Self

from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui  import QPainter, QPen

from .....app import settings

from .....core.defs import PITCH

from ..diagram import DiagramScene

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...items.symbol import SymbolDefinitionItem


class SymbolScene(DiagramScene):
    """Scene for editing a single symbol."""

    # instance attributes
    _symbol : "SymbolDefinitionItem" | None  # symbol being edited
    _brect  : QRectF | None        # bounding rect of all items

    def __init__(
        self   : Self,
        symbol : "SymbolDefinitionItem" | None = None
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

    def drawBackground(
        self    : Self,
        painter : QPainter,
        rect    : QRectF
    ) -> None:
        super().drawBackground(painter, rect)
        if self._brect is not None:
            pen = QPen(settings().get("theme/border"), 0, Qt.PenStyle.DashLine)
            painter.save()
            painter.setPen(pen)
            painter.drawRect(self._brect)
            painter.restore()
