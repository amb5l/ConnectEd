from __future__ import annotations

from typing import Self

from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui  import QImage, QPainter

from ......core.check import checked

from ..host import asDiagramScene


_BITMAP_MAX_PX = 2048


class DiagramSceneApiUtilMixin:
    """Utility methods for diagram scenes."""

    def allRect(self : Self) -> QRectF:
        host = asDiagramScene(self)
        return host.itemsBoundingRect().united(host._sheet_rect)

    @checked
    def bitmap(self : Self) -> QImage:
        """
        Render the scene to a raster image suitable for PNG export.

        Diagram scenes use the sheet rectangle; other scenes use the union of
        item bounds when empty. Pixel size matches scene
        units up to ``_BITMAP_MAX_PX`` on the longest side.
        """
        host = asDiagramScene(self)
        source = host.allRect()
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
        host.hideGrips()
        try:
            host.render(painter, target, source)
        finally:
            host.updateGrips()
        painter.end()
        return image
