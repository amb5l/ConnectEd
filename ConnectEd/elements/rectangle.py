from typing import ClassVar, Optional

from PyQt6.QtCore    import QRectF, QPointF, Qt
from PyQt6.QtGui     import QPainter, QPen, QBrush, QPainterPath
from PyQt6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget

from ..core import Z_DRAWING, settings, Rect2

from . import Element, LineSpec, FillSpec

class Rectangle(Element):
    Z    : ClassVar[int] = Z_DRAWING
    rect : Rect2
    line : LineSpec
    fill : FillSpec

    def __init__(
        self     : 'Rectangle',
        p1       : QPointF,
        p2       : Optional[QPointF] = None,
        line     : Optional[LineSpec] = None,
        fill     : Optional[FillSpec] = None,
        selected : bool = False,
        wip      : bool = False
    ) -> None:
        super().__init__(selected, wip)
        self.rect = Rect2(p1, p2)
        self.line = line
        self.fill = fill

        # Explicitly set flags to ensure visibility
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemClipsToShape, False)
        self.setCacheMode(QGraphicsItem.CacheMode.NoCache)

    def setPoint2(self : 'Rectangle', p2 : QPointF) -> None:
        self.rect.setPoint2(p2)
        # Update scene if possible
        if self.scene():
            self.scene().update()

    def boundingRect(self) -> QRectF:
        # Use a MUCH more generous margin to prevent culling during extreme zoom
        # The minimum margin is 20 pixels or the rectangle's width/height if larger
        baseRect = self.rect
        margin = max(20.0, baseRect.width() / 2, baseRect.height() / 2)
        return baseRect.adjusted(-margin, -margin, margin, margin)

    def shape(self) -> QPainterPath:
        path = QPainterPath()
        # Use the same generous margin as boundingRect
        baseRect = self.rect
        margin = max(20.0, baseRect.width() / 2, baseRect.height() / 2)
        path.addRect(baseRect.adjusted(-margin, -margin, margin, margin))
        return path

    def paint(
        self    : 'Rectangle',
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        # Save painter state
        painter.save()

        # Configure pen and brush using settings
        self.setPenBrush(
            painter,
            settings.prefs.display.elements.rectangle,
            settings.theme.elements.rectangle
        )

        # Draw the rectangle
        painter.drawRect(self.rect)

        # Restore painter state
        painter.restore()
