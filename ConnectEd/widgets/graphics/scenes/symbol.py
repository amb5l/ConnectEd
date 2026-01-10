from typing import Self

from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui  import QPainter, QPen

from ....app import settings

from ....core.utils import registerClass

from ....core.defs import PITCH

from .drawing import DrawingScene


class SymbolScene(DrawingScene):

    # instance attributes
    _brect   : QRectF | None  # bounding rect of all items

    def __init__(self : Self) -> None:
        super().__init__()
        self._brect = None
        self.onChange()
        self.changed.connect(self.onChange)

    def onChange(self : Self) -> None:
        from ..items.symbol_pin    import SymbolPin
        from ..items.property_text import PropertyTextMixin
        from ..items.line          import Line
        from ..items.rectangle     import Rectangle
        from ..items.polyline      import Polyline
        from ..items.text          import TextLine, TextBlock
        classes = (
            SymbolPin, PropertyTextMixin, \
            Line, Rectangle, Polyline, TextLine, TextBlock
        )
        # get bounding rect of all items
        rect = self.itemsBoundingRect()
        # expand size if too small
        rect.setWidth(min(rect.size().width(), PITCH))
        rect.setHeight(min(rect.size().height(), PITCH))
        # store result
        self._brect = rect

    def drawBackground(
        self    : Self,
        painter : QPainter,
        rect    : QRectF
    ) -> None:
        super().drawBackground(painter, rect)
        if self._brect is not None:
            pen = QPen(settings().get("theme/border"), 0, Qt.PenStyle.DashLine)
            painter.save()
            painter.setPen(pen)
            painter.drawRect(self._brect)
            painter.restore()
