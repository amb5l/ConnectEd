__all__ = ['Rectangle']

from PyQt6.QtCore import QPointF, QSizeF

from ...core import Z_DRAWING

from . import RectItem, KeyPoint


class Rectangle(RectItem):
    Z = Z_DRAWING

    def __init__(
        self   : 'Rectangle',
        pos    : QPointF,
        size   : QSizeF = QSizeF(0, 0),
        anchor : KeyPoint = KeyPoint.TOP_LEFT
    ) -> None:
        super().__init__(pos, size, anchor)
