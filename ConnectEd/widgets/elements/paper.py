__all__ = ['Paper']

from typing import Optional

from PyQt6.QtCore import QPointF, QRectF, QSizeF, \
                         QXmlStreamWriter, QXmlStreamReader

from ...core import Z_PAPER, value2str, str2value

from ... import hub

from . import RectElement


class Paper(RectElement):
    XML_ATTRIBUTES = RectElement.XML_ATTRIBUTES | {
        'paper_size' : ( lambda self, value: self.setSheetSize(value) , lambda self: self.getSheetSize() )
    }

    Z = Z_PAPER

    paper_size : str

    def __init__(
        self       : 'Paper',
        paper_size : Optional[str] = None,
        pen_spec   : bool = False,
        brush_spec : bool = True
    ) -> None:
        super().__init__(pen_spec=pen_spec, brush_spec=brush_spec)
        if paper_size is None:
            paper_size = hub.settings.defaults.paper_size
        self.setSheetSize(paper_size)
        self.setZValue(Z_PAPER)

    def setSheetSize(self : 'Paper', paper_size : str) -> None:
        self.paper_size = paper_size
        size = getattr(hub.settings.paper_sizes, paper_size)
        self.setSize(QSizeF(size.width(), size.height()))

    def getSheetSize(self : 'Paper') -> str:
        return self.paper_size
