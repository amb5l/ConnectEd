# shared guides

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QGraphicsLineItem
from PyQt6.QtGui     import QPen

from .....app import settings

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import DrawingScene


class DrawingSceneGuidesMixin:
    """Shared guides."""

    _guides : list[QGraphicsLineItem] = []

    def initGuides(self : "DrawingScene") -> None:
        self._guides = []

    def guide(self : "DrawingScene", index : int) -> QGraphicsLineItem:
        while len(self._guides) <= index:
            self._guides.append(self._newGuide())
        return self._guides[index]

    def _newGuide(self : "DrawingScene") -> QGraphicsLineItem:
        guide = QGraphicsLineItem()
        spec = settings().get("theme/selected/line")
        color = spec.color if hasattr(spec, "color") else spec
        pen = QPen(color, 0, Qt.PenStyle.DotLine)
        guide.setPen(pen)
        self.addItem(guide)
        return guide
