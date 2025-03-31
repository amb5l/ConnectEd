__all__ = ['Border']

from typing import Optional

from PyQt6.QtCore    import QPointF, QSizeF, QXmlStreamWriter

from ...core import Z_TEMPLATE, value2str
from .       import RectItem, Paper

from ... import hub

class Border(RectItem):
    Z = Z_TEMPLATE

    margin : float

    def __init__(
        self     : 'Border',
        paper    : 'Paper',
        margin   : Optional[float] = None
    ) -> None:
        super().__init__(QPointF(0, 0), fill=False)
        self.paper = paper
        if margin is None:
            margin = hub.settings.defaults.margin
        self.setMargin(margin)

    def setMargin(self, margin : float) -> None:
        self.margin = margin
        self.updateSize()

    def updateSize(self : 'Border') -> None:
        self.setPosSize(
            QPointF(self.margin, self.margin),
            QSizeF(
                self.paper.rect().width()  - (2 * self.margin),
                self.paper.rect().height() - (2 * self.margin)
            )
        )

    def toXml(self : 'Border', xw : QXmlStreamWriter) -> None:
        xw.writeStartElement('Border')
        xw.writeAttribute('margin', value2str(self.margin))
        xw.writeEndElement()
