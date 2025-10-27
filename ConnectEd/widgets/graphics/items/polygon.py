from typing import Self

from PyQt6.QtGui import QPainterPath

from .polyline import Polyline

from .mixin.fill import ItemFillMixin


class Polygon(ItemFillMixin, Polyline):
    def updateVertices(self : Self) -> None:
        path = QPainterPath()
        path.moveTo(self._vertices[0].pos())
        for vertex in self._vertices[1:]:
            path.lineTo(vertex.pos())
        path.closeSubpath()
        self.setPath(path)
