from typing import Self

from PyQt6.QtGui  import QPainterPath

from .....core.check import checked


class ItemShapeMixin:
    # instance attributes
    _hshape : QPainterPath  # hit detect shape

    @checked
    def initShape(self : Self) -> None:
        self._hshape = QPainterPath()

    def shape(self : Self) -> QPainterPath:
        return self._hshape
