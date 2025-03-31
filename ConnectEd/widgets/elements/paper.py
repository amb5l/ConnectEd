__all__ = ['Paper']

from PyQt6.QtCore    import QPointF, QSizeF, QXmlStreamWriter

from ...core import Z_PAPER, value2str

from ... import hub

from . import RectElement


class Paper(RectElement):
    Z = Z_PAPER

    size_name : str

    def __init__(self : 'Paper', size : str):
        super().__init__(QPointF(0, 0), pen_spec=False)
        self.setZValue(Z_PAPER)
        self.setSize(size)

    def setSize(self : 'Paper', size_name : str) -> None:
        self.size_name = size_name
        size = getattr(hub.settings.sheet_sizes, size_name)
        self.setPosSize(QPointF(0, 0), QSizeF(size.width(), size.height()))

    def toXml(self : 'Paper', xw : QXmlStreamWriter) -> None:
        xw.writeStartElement('Paper')
        xw.writeAttribute('rect', value2str(self.rect()))
        xw.writeEndElement()
