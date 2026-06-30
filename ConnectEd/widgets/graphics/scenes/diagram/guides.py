# shared guides

from __future__ import annotations

from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QGraphicsLineItem
from PyQt6.QtGui     import QPen

from .....app import settings


class DiagramSceneGuidesMixin:
    """Shared guides."""

    _guides : list[QGraphicsLineItem] = []

    def initGuides(self : Self) -> None:
        self._guides = []

    def guide(self : Self, index : int) -> QGraphicsLineItem:
        while len(self._guides) <= index:
            self._guides.append(self._newGuide())
        return self._guides[index]

    def _newGuide(self : Self) -> QGraphicsLineItem:
        from . import DiagramScene
        if not isinstance(self, DiagramScene): raise TypeError("Bad host")
        guide = QGraphicsLineItem()
        spec = settings().get("theme/selected/line")
        color = spec.color if hasattr(spec, "color") else spec
        pen = QPen(color, 0, Qt.PenStyle.DotLine)
        guide.setPen(pen)
        self.addItem(guide)
        return guide
