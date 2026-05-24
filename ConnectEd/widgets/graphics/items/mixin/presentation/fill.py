from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsView
from PyQt6.QtGui     import QColor, QBrush

from ......app import logger

from ......core.check import checked
from ......core.types import NoChange, NO_CHANGE

from ....scenes import withScene

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....scenes.drawing import DrawingScene

from . import ItemType


class ItemPresentationFillMixin:

    # API

    def hasFill(self : "Self | ItemType") -> bool:
        return self.hasFillColor() or self.hasFillStyle()

    def hasFillColor(self : "Self | ItemType") -> bool:
        return hasattr(self, "_fill_color")

    def fillColor(self : "Self | ItemType") -> QColor | None:
        return self._fill_color if hasattr(self, "_fill_color") else None

    def defaultFillColor(
        self   : "Self | ItemType",
        widget : "QGraphicsView | None" = None
    ) -> QColor | None:
        scene = self._defaultScene(widget)
        key = self._brushKeyDefault()
        brush = scene.resources.brush(self.resourcesName(), key)
        return brush.color()

    @checked
    def setFillColor(self : "Self | ItemType", color: QColor | None | NoChange) -> None:
        if color is NO_CHANGE:
            return
        if not hasattr(self, "_fill_color"):
            logger().error("This item does not support fill color overrides.")
            return
        self._fill_color = color
        self._updateBrush()
        if hasattr(self, "properties"):
            self.properties.signalChanges("Fill Color")

    def hasFillStyle(self : "Self | ItemType") -> bool:
        return hasattr(self, "_fill_style")

    def fillStyle(self : "Self | ItemType") -> Qt.BrushStyle | None:
        return self._fill_style if hasattr(self, "_fill_style") else None

    def defaultFillStyle(
        self   : "Self | ItemType",
        widget : "QGraphicsView | None" = None
    ) -> Qt.BrushStyle | None:
        scene = self._defaultScene(widget)
        key = self._brushKeyDefault()
        brush = scene.resources.brush(self.resourcesName(), key)
        return brush.style()

    @checked
    def setFillStyle(self : "Self | ItemType", style: Qt.BrushStyle | None | NoChange) -> None:
        if style is NO_CHANGE:
            return
        if not hasattr(self, "_fill_style"):
            logger().error("This item does not support fill style overrides.")
            return
        self._fill_style = style
        self._updateBrush()
        if hasattr(self, "properties"):
            self.properties.signalChanges("Fill Style")

    # helpers

    def _brushKey(self : Self | QGraphicsItem) -> bool:
        return self.isSelected()

    def _brushKeyDefault(self : Self) -> bool:
        return False

    def _updateBrush(self : Self, _scene : "DrawingScene") -> None:
        raise NotImplementedError("Not wired!")

    @withScene
    def _updateBrushFast(
        self : "Self | ItemType",
        scene : "DrawingScene"
    ) -> None:
        brush = scene.resources.brush(self.resourcesName(), self._brushKey())
        self.setBrush(brush)

    @withScene
    def _updateBrushSlow(
        self  : "Self | ItemType",
        scene : "DrawingScene"
    ) -> None:
        brush = scene.resources.brush(self.resourcesName(), self._brushKey())
        override_color = \
            hasattr(self, "_fill_color") and not self.isSelected() \
                and self._fill_color is not None
        override_style = \
            hasattr(self, "_fill_style") and self._fill_style is not None
        if override_color or override_style:
            brush = QBrush(brush)
            if override_color: brush.setColor(self._fill_color)
            if override_style: brush.setStyle(self._fill_style)
        self.setBrush(brush)