__all__ = ['Extents']

from PyQt6.QtCore    import QPointF, QRectF, QSizeF, \
                            QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtGui     import QPainter, QPen, QBrush, QColor
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsRectItem, \
                            QWidget, QStyleOptionGraphicsItem

from ...core import Z_EXTENTS, value2str, str2value

from ... import hub


class Extents(QGraphicsRectItem):
    """Extents of a drawing - the outer limit!"""

    Z = Z_EXTENTS

    def __init__(self : 'Extents', sheet_or_rect : str | QRectF) -> None:
        if isinstance(sheet_or_rect, str):
            paper_size = getattr(hub.settings.paper_sizes, sheet_or_rect)
            size = QSizeF(paper_size.width(), paper_size.height())
            super().__init__(QRectF(
                -QPointF(size.width(), size.height()),
                QSizeF(size.width() * 3, size.height() * 3)
            ))
        elif isinstance(sheet_or_rect, QRectF):
            super().__init__(sheet_or_rect)
        else:
            raise ValueError(f'Bad size_or_rect: {sheet_or_rect}')
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
            hub.settings.prefs.display.elements.extents.line.width,
            hub.settings.prefs.display.elements.extents.line.style
        ))
        painter.setBrush(QBrush(
            QColor(hub.settings.theme.extents.fill),
            hub.settings.prefs.display.elements.extents.fill
        ))
        super().paint(painter, option, widget)

    def toXml(self, xw : QXmlStreamWriter) -> None:
        xw.writeStartElement('Extents')
        xw.writeAttribute('rect', value2str(self.rect()))
        xw.writeEndElement()

    @classmethod
    def fromXml(cls, xr: QXmlStreamReader) -> 'Extents':
        rect = str2value(xr.attributes().value('rect'))
        instance = cls(rect)
        xr.readNext()
        return instance
