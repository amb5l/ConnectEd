from typing import Self

from PyQt6.QtCore import QRectF


class ElementBoundMixin:
    # instance attributes
    _brect  : QRectF       # bounding rect

    def initBound(self : Self) -> None:
        self._brect  = QRectF()

    def boundingRect(self : Self) -> QRectF:
        return self._brect
