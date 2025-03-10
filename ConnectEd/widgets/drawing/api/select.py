from enum import Enum, auto

from PyQt6.QtCore import QPointF, QRectF

from ...items import Item

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import Drawing


class DrawingApiSelectMixin:
    class SelectOperation(Enum):
        Fresh  = auto()
        Toggle = auto()
        Add    = auto()
        Remove = auto()

    def selectPoint(
        self      : 'Drawing',
        lpos      : QPointF,
        operation : SelectOperation = SelectOperation.Fresh
    ) -> None:
        candidates = []
        for item in self.items:
            if item.
        item.selected = True
        self.update()

    def selectWindow(
        self      : 'Drawing',
        lrect     : QRectF,
        intersect : bool = True,
        operation : SelectOperation = SelectOperation.Toggle
    ) -> None:
        pass

    def selectAll(self : 'Drawing') -> None:
        pass

    def selectNone(self, item : Item) -> None:
        item.selected = False
