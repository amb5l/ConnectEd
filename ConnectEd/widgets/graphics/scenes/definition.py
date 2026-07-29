from typing import Self, TypeVar, Generic

from PyQt6.QtCore    import QRectF
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtGui     import QPainter

from ....app import settings

from ....core.check import checked
from ....core.defs  import PITCH

from .diagram import DiagramScene


TItem = TypeVar("TItem", bound=QGraphicsItem)


class DefinitionScene(DiagramScene, Generic[TItem]):
    """Scene for editing a single block definition."""

    # instance attributes
    _item : TItem | None  # definition being edited

    @checked
    def __init__(
        self : Self,
        item : TItem | None = None
    ) -> None:
        super().__init__()
        self._item = item
        if item is not None:
            self.addItem(item)

    def item(self : Self) -> TItem | None:
        return self._item

    def setItem(self : Self, item : TItem | None) -> None:
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
