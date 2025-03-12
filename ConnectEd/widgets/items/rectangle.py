from typing import Optional

from PyQt6.QtCore    import QPointF

from ...core import Z_DRAWING

from . import RectPenBrushItem, Anchor


class Rectangle(RectPenBrushItem):
    Z = Z_DRAWING

    def __init__(
        self   : 'Rectangle',
        p1     : QPointF,
        p2     : Optional[QPointF] = None,
        anchor : Anchor = Anchor.TOP_LEFT,
        wip    : bool = False
    ) -> None:
        super().__init__(p1, p2, anchor)
        self.setWIP(wip)
