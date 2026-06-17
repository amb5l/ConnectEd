from __future__ import annotations

from typing import Self, TypeAlias

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui  import QImage, QPainter

from ......app import settings

from ......core.check import checked

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingScene
    MixinSelf: TypeAlias = Self | DrawingScene
else:
    MixinSelf = Self


_BITMAP_MAX_PX = 2048


class DrawingSceneApiUtilMixin:
    """Utility methods for drawing scenes."""

    @checked
    def bitmap(self : MixinSelf) -> QImage:
        """
        Render the scene to a raster image suitable for PNG export.

        Diagram scenes use the sheet rectangle; other scenes use the union of
        item bounds, or default extents when empty. Pixel size matches scene
        units up to ``_BITMAP_MAX_PX`` on the longest side.
        """
        source = self._bitmapSourceRect()
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

    def _bitmapSourceRect(self : MixinSelf) -> QRectF:
        sheet = getattr(self, "sheet", None)
        if sheet is not None:
            return QRectF(sheet.rect)
        items_rect = self._bitmapItemsRect()
        if items_rect is not None and not items_rect.isEmpty():
            return items_rect
        return QRectF(QPointF(0.0, 0.0), settings().get("defaults/extents"))

    def _bitmapItemsRect(self : MixinSelf) -> QRectF | None:
        items_rect : QRectF | None = None
        for item in self.items():
            item_rect = item.mapToScene(item.boundingRect()).boundingRect()
            if items_rect is None:
                items_rect = item_rect
            else:
                items_rect = items_rect.united(item_rect)
        return items_rect
