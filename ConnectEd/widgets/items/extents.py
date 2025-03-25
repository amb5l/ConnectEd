__all__ = ['Extents']

from PyQt6.QtCore    import QPointF, QRectF, QSizeF
from PyQt6.QtGui     import QPainter, QPen, QBrush, QColor
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsRectItem, \
                            QWidget, QStyleOptionGraphicsItem

from ...core import Z_EXTENTS

from ... import hub


class Extents(QGraphicsRectItem):
    """Extents of a drawing - the outer limit!"""

    Z = Z_EXTENTS

    def __init__(self : 'Extents', sheet : str) -> None:
        sheet_size = getattr(hub.settings.sheet_sizes, sheet)
        super().__init__(QRectF(
            -QPointF(sheet_size.width(), sheet_size.height()),
            QSizeF(sheet_size.width() * 3, sheet_size.height() * 3)
        ))
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setZValue(self.Z)

    def paint(
        self    : 'Extents',
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        painter.setPen(QPen(
            QColor(hub.settings.theme.extents.line),
            hub.settings.prefs.display.items.extents.line.width,
            hub.settings.prefs.display.items.extents.line.style
        ))
        painter.setBrush(QBrush(
            QColor(hub.settings.theme.extents.fill),
            hub.settings.prefs.display.items.extents.fill
        ))
        super().paint(painter, option, widget)
