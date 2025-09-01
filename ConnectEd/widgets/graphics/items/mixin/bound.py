from typing import Self

from PyQt6.QtCore import QRectF
from PyQt6.QtGui  import QPainterPath


class ElementBoundShapeMixin:
    # instance attributes
    _brect  : QRectF       # bounding rect
    _hshape : QPainterPath # hit detect shape

    def initBoundShape(self : Self) -> None:
        self._brect  = QRectF()
        self._hshape = QPainterPath()

    def boundingRect(self : Self) -> QRectF:
        return self._brect

    def shape(self : Self) -> QPainterPath:
        return self._hshape
