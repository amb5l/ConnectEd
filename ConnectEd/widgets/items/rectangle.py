from typing import Optional

from PyQt6.QtCore    import QRectF, QPointF
from PyQt6.QtGui     import QPainter
from PyQt6.QtWidgets import QStyleOptionGraphicsItem, QWidget

from ...core import Z_DRAWING, settings

from . import RectPenBrushItem, ItemWIPMixin, Anchor


class Rectangle(RectPenBrushItem, ItemWIPMixin):
    Z = Z_DRAWING

    def __init__(
        self     : 'Rectangle',
        p1       : QPointF,
        p2       : Optional[QPointF] = None,
        anchor   : Anchor = Anchor(),
        wip      : bool = False
    ) -> None:
        super().__init__(p1, p2, anchor)
        ItemWIPMixin.__init__(self, wip)
