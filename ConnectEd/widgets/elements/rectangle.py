__all__ = ['Rectangle']

from PyQt6.QtCore import QPointF, QSizeF

from ...core import Z_DRAWING

from . import KeyPoint

from .base_rect import BaseRectangle


class Rectangle(BaseRectangle):
    Z = Z_DRAWING

    def __init__(
        self   : 'Rectangle',
        pos    : QPointF = QPointF(0, 0),
        size   : QSizeF = QSizeF(0, 0),
        anchor : KeyPoint = KeyPoint.TOP_LEFT
    ) -> None:
        super().__init__(pos, size, anchor)
