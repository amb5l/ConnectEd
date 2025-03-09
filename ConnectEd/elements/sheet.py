from typing import ClassVar

from PyQt6.QtCore    import QPointF, QRectF
from PyQt6.QtWidgets import QStyleOptionGraphicsItem, QWidget
from PyQt6.QtGui     import QPainter

from ..core import Z_SHEET, settings

from . import Element


class Sheet(Element):
    Z         : ClassVar[int] = Z_SHEET
    size_name : str
    rect      : QRectF

    def __init__(self, size : str):
        super().__init__()
        self.setSize(size)
        self.setZValue(Z_SHEET)

    def setSize(self, size_name : str) -> None:
        self.size_name = size_name
        self.rect = QRectF(
            QPointF(0, 0),
            getattr(settings.sheet_sizes, size_name)
        )

    def boundingRect(self) -> QRectF:
        return self.rect

    def paint(
        self    : 'Sheet',
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        painter.fillRect(self.rect, settings.theme.sheet)
