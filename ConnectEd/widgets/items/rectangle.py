from PyQt6.QtCore import QPointF, QSizeF

from ...core import Z_DRAWING

from . import RectItem, Anchor


class Rectangle(RectItem):
    Z = Z_DRAWING

    def __init__(
        self   : 'Rectangle',
        pos    : QPointF,
        size   : QSizeF = QSizeF(0, 0),
        anchor : Anchor = Anchor.TOP_LEFT,
        wip    : bool = False
    ) -> None:
        super().__init__(pos, size, anchor, wip)
