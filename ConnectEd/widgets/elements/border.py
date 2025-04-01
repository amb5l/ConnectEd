__all__ = ['Border']

from typing import Optional

from PyQt6.QtCore import QPointF, QSizeF

from ...core import Z_TEMPLATE
from .       import Paper

from ... import hub

class Border(Paper):
    XML_ATTRIBUTES = Paper.XML_ATTRIBUTES | {
        'margin'     : ( lambda self, value: self.setMargin(value)    , lambda self: self.getMargin()    )
    }
    Z = Z_TEMPLATE

    margin     : float

    def __init__(
        self       : 'Border',
        paper_size : Optional[str] = None,
        margin     : Optional[float] = None
    ) -> None:
        super().__init__(pen_spec=True, brush_spec=False)
        if paper_size is None:
            paper_size = hub.settings.defaults.paper_size
        if margin is None:
            margin = hub.settings.defaults.margin
        self.update(paper_size, margin)

    def setMargin(self : 'Border', margin : float) -> None:
        self.margin = margin
        self.update()

    def getMargin(self : 'Border') -> float:
        return self.margin

    def update(
        self       : 'Border',
        paper_size : Optional[str] = None,
        margin     : Optional[float] = None
    ) -> None:
        if paper_size:
            self.paper_size = paper_size
        if margin:
            self.margin = margin
        size = getattr(hub.settings.paper_sizes, self.paper_size)
        self.setPosSize(
            QPointF(self.margin, self.margin),
            QSizeF(
                size.width()  - (2 * self.margin),
                size.height() - (2 * self.margin)
            )
        )
