from __future__ import annotations

from typing import Self

from PyQt6.QtCore    import QRectF
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem
from PyQt6.QtGui     import QPainter

from ...app import settings

from ...core.check import checked

from ...domains.hdl.schematic.library import HdlSchematicLibrary

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .browser import LibraryBrowser


_MARGIN = 5


class LibraryPreviewPane(QGraphicsView):
    _library : HdlSchematicLibrary
    _scene   : QGraphicsScene

    @checked
    def __init__(
        self    : Self,
        library : HdlSchematicLibrary,
        parent  : LibraryBrowser | None = None
    ) -> None:
        super().__init__(parent)
        self._library = library
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

    def drawBackground(
        self    : Self,
        painter : QPainter | None,
        rect    : QRectF
    ) -> None:
        if painter is None:
            return
        painter.fillRect(rect, settings().get("theme/background"))

    @checked
    def setDefinition(self : Self, definition : QGraphicsItem | None) -> None:
        self._scene.clear()
        if definition is None:
            return
        self._scene.addItem(definition)
        self._fitItem(definition)

    @checked
    def _fitItem(self : Self, item : QGraphicsItem) -> None:
        rect = item.sceneBoundingRect()
        if rect.isEmpty():
            return
        viewport = self.viewport()
        if viewport is None:
            return
        width  = viewport.width()  - 2 * _MARGIN
        height = viewport.height() - 2 * _MARGIN
        if width <= 0 or height <= 0:
            return
        if rect.width() <= 0 or rect.height() <= 0:
            return
        self.resetTransform()
        scale = min(width / rect.width(), height / rect.height())
        self.scale(scale, scale)
        self.centerOn(rect.center())
