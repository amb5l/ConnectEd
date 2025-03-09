from enum import Enum, auto

from PyQt6.QtCore import QPointF, QRectF

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
        for element in self.elements:
            if element.
        element.selected = True
        self.update()

    def selectWindow(
        self      : 'Drawing',
        lrect     : QRectF,
        intersect : bool = True,
        operation : SelectOperation = SelectOperation.Toggle
    ) -> None:
        pass

    def selectAll(self : 'Drawing') -> None:

    def selectNone(self, element : Element) -> None:
        element.selected = False
