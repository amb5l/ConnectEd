from __future__ import annotations

from typing import Self

from PyQt6.QtCore    import QRectF
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem, \
                            QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui     import QPainter

from ...app                           import settings

from ...core.check                    import checked

from ...domains.hdl.schematic.library import HdlSchematicLibrary

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...widgets.graphics.items.symbol import SymbolDefinitionItem
    from .browser                         import LibraryBrowser


_MARGIN = 5


class LibraryPreviewScene(QGraphicsScene):
    _symbol : SymbolDefinitionItem | None = None

    def symbol(self : Self) -> SymbolDefinitionItem | None:
        return self._symbol

    def setSymbol(self : Self, symbol : SymbolDefinitionItem | None) -> None:
        self.clear()
        self._symbol = symbol
        if symbol is None:
            return
        self.addItem(symbol)


class LibraryPreviewView(QGraphicsView):
    def __init__(self : Self, parent : QWidget | None = None) -> None:
        super().__init__(parent)

    def update(self : Self) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        scene = self.scene()
        if not isinstance(scene, LibraryPreviewScene):
            raise RuntimeError("Bad scene")
        symbol = scene.symbol()
        if symbol is None:
            return
        rect = symbol.sceneBoundingRect()
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

    def drawBackground(
        self    : Self,
        painter : QPainter | None,
        rect    : QRectF
    ) -> None:
        if painter is None:
            return
        painter.fillRect(rect, settings().get("theme/background"))

    @checked
    def setSymbol(self : Self, symbol : SymbolDefinitionItem | None) -> None:
        scene = self.scene()
        if not isinstance(scene, LibraryPreviewScene):
            raise RuntimeError("Bad scene")
        scene.setSymbol(symbol)
        self.update()


class LibraryPreviewPane(QWidget):
    _library : HdlSchematicLibrary
    _layout  : QVBoxLayout
    _title   : QLabel
    _view    : LibraryPreviewView
    _scene   : QGraphicsScene

    @checked
    def __init__(
        self    : Self,
        library : HdlSchematicLibrary,
        parent  : LibraryBrowser | None = None
    ) -> None:
        super().__init__(parent)
        self._library = library
        self._layout = QVBoxLayout(self)
        self._title = QLabel("Preview")
        self._layout.addWidget(self._title)
        self._view = LibraryPreviewView(self)
        self._scene = QGraphicsScene(self)
        self._view.setScene(self._scene)
        self._layout.addWidget(self._view)
        self.setLayout(self._layout)

    @checked
    def setSymbol(self : Self, symbol : SymbolDefinitionItem | None) -> None:
        self._view.setSymbol(symbol)
