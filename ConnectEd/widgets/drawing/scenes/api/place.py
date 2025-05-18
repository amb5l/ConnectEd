__all__ = ["DrawingApiPlaceMixin"]

from typing import overload, Optional

from PyQt6.QtCore import QRectF, QPointF, QSizeF

from ... import Rectangle, TextBlock

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import Drawing


class DrawingApiPlaceMixin:

    @overload
    def placeRectangle(self : "Drawing", rect : QRectF) -> None:
        ...

    @overload
    def placeRectangle(
        self : "Drawing",
        pos  : QPointF,
        size : QSizeF
    ) -> None:
        ...

    @overload
    def placeRectangle(
        self : "Drawing",
        x    : float,
        y    : float,
        w    : float,
        h    : float
    ) -> None:
        ...

    def placeRectangle(
        self              : "Drawing",
        rect_or_pos_or_ax : QRectF | QPointF | float = QRectF(),
        size_or_ay        : Optional[QSizeF | float] = None,
        w                 : Optional[float]          = None,
        h                 : Optional[float]          = None
    ) -> None:
        if isinstance(rect_or_pos_or_ax, QRectF):
            item = Rectangle(rect_or_pos_or_ax)
        elif isinstance(rect_or_pos_or_ax, QPointF):
            item = Rectangle(rect_or_pos_or_ax, size_or_ay)
        else:
            item = Rectangle(rect_or_pos_or_ax, size_or_ay, w, h)
        self.addItem(item)

    @overload
    def placeTextBlock(
        self : "Drawing",
        text : str,
        pos  : QPointF
    ) -> None:
        ...

    @overload
    def placeTextBlock(
        self : "Drawing",
        text : str,
        x    : float,
        y    : float
    ) -> None:
        ...

    def placeTextBlock(
        self      : "Drawing",
        text      : str,
        pos_or_x  : QPointF | float = QPointF(),
        y         : Optional[float] = None
    ) -> None:
        if isinstance(pos_or_x, QPointF):
            item = TextBlock(text, pos_or_x)
        else:
            item = TextBlock(text, pos_or_x, y)
        self.addItem(item)
