from typing import Optional

from PyQt6.QtCore    import QPointF
from PyQt6.QtGui     import QPainter
from PyQt6.QtWidgets import QStyleOptionGraphicsItem, QWidget

from ...core import Z_TEMPLATE, settings
from .       import RectPenOnlyItem, Paper

class Border(RectPenOnlyItem):
    Z = Z_TEMPLATE

    margin : float

    def __init__(
        self     : 'Border',
        paper    : 'Paper',
        margin   : Optional[float] = None
    ) -> None:
        super().__init__(QPointF(0, 0))
        self.paper = paper
        if margin is None:
            margin = settings.defaults.margin
        self.setMargin(margin)

    def setMargin(self, margin : float) -> None:
        self.margin = margin
        self.updateSize()

    def updateSize(self : 'Border') -> None:
        self.setPoints(
            QPointF(self.margin, self.margin),
            QPointF(
                self.paper.rect().width() - self.margin,
                self.paper.rect().height() - self.margin
            )
        )

    def paint(
        self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        print('Border.paint', self.rect())
        super().paint(painter, option, widget)
