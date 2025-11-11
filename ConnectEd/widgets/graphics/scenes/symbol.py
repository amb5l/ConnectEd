from typing import Self

from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui  import QPainter, QPen

from ....app import settings

from ....core.defs import PITCH

from ..items.handle import Handle

from .drawing import DrawingScene


class SymbolScene(DrawingScene):

    # instance attributes
    _brect   : QRectF | None

    def __init__(self : Self) -> None:
        super().__init__()
        self._brect = None
        self.onChange()
        self.changed.connect(self.onChange)

    def onChange(self : Self) -> None:
        from ..items.line            import Line
        from ..items.base_rect       import BaseRectangleMixin  # rectangle, ellipse
        from ..items.polyline        import Polyline
        from ..items.base_text       import BaseText
        from ..items.base_text_block import BaseTextBlock
        # get bounding rect of all items
        rect = QRectF()
        for item in self.items():
            types = (Line, BaseRectangleMixin, Polyline, BaseText, BaseTextBlock)
            if isinstance(item, types):
                rect = rect.united(item.sceneTightBoundingRect())
        # expand size if too small
        wa = PITCH - rect.size().width()
        ha = PITCH - rect.size().height()
        if wa > 0:
            rect.setX(rect.x() - (wa / 2))
            rect.setWidth(PITCH)
        if ha > 0:
            rect.setY(rect.y() - (ha / 2))
            rect.setHeight(PITCH)
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
