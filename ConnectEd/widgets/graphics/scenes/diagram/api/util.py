from __future__ import annotations

from typing import Self

from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui  import QImage, QPainter

from ......core.check import checked


_BITMAP_MAX_PX = 2048


class DiagramSceneApiUtilMixin:
    """Utility methods for diagram scenes."""

    def allRect(self : Self) -> QRectF:
        from .. import DiagramScene
        if not isinstance(self, DiagramScene): raise TypeError("Bad host")
        return self.itemsBoundingRect().united(self._sheet_rect)

    @checked
    def bitmap(self : Self) -> QImage:
        """
        Render the scene to a raster image suitable for PNG export.

        Diagram scenes use the sheet rectangle; other scenes use the union of
        item bounds when empty. Pixel size matches scene
        units up to ``_BITMAP_MAX_PX`` on the longest side.
        """
        from .. import DiagramScene
        if not isinstance(self, DiagramScene): raise TypeError("Bad host")
        source = self.allRect()
        width  = max(1.0, source.width())
        height = max(1.0, source.height())
        scale  = min(
            1.0,
            _BITMAP_MAX_PX / width,
            _BITMAP_MAX_PX / height,
        )
        px_w = max(1, int(width  * scale))
        px_h = max(1, int(height * scale))

        image = QImage(px_w, px_h, QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.transparent)

        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        target = QRectF(0.0, 0.0, px_w, px_h)
        self.hideGrips()
        try:
            self.render(painter, target, source)
        finally:
            self.updateGrips()
        painter.end()
        return image
