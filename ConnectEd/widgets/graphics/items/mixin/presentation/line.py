from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QGraphicsView
from PyQt6.QtGui     import QPen, QColor

from ......app import logger

from ......core.check import checked
from ......core.types import NoChange, NO_CHANGE

from ....scenes import withScene

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....scenes.drawing import DrawingScene

from . import ItemType


class ItemPresentationLineMixin:

    # API

    def hasLine(self : "Self | ItemType") -> bool:
        return self.hasLineColor() or self.hasLineWidth() or self.hasLineStyle()

    def hasLineColor(self : "Self | ItemType") -> bool:
        return hasattr(self, "_line_color")

    def defaultLineColor(
        self   : "Self | ItemType",
        widget : "QGraphicsView | None" = None
    ) -> QColor | None:
        scene = self._defaultScene(widget)
        key = self._penKeyDefault()
        pen = scene.resources.pen(self.resourcesName(), key)
        return pen.color()

    def lineColor(self : "Self | ItemType") -> QColor | None:
        return self._line_color if hasattr(self, "_line_color") else None

    @checked
    def setLineColor(self : "Self | ItemType", color: QColor | None | NoChange) -> None:
        if color is NO_CHANGE:
            return
        if not hasattr(self, "_line_color"):
            logger().error("This item does not support line color overrides.")
            return
        self._line_color = color
        self._updatePen()

    def hasLineWidth(self : "Self | ItemType") -> bool:
        return hasattr(self, "_line_width")

    def lineWidth(self : "Self | ItemType") -> float | None:
        return self._line_width if hasattr(self, "_line_width") else None

    def defaultLineWidth(
        self   : "Self | ItemType",
        widget : "QGraphicsView | None" = None
    ) -> float | None:
        scene = self._defaultScene(widget)
        key = self._penKeyDefault()
        pen = scene.resources.pen(self.resourcesName(), key)
        return pen.widthF()

    @checked
    def setLineWidth(self : "Self | ItemType", width: float | None | NoChange) -> None:
        if width is NO_CHANGE:
            return
        if not hasattr(self, "_line_width"):
            logger().error("This item does not support line width overrides.")
            return
        self._line_width = width
        self._updatePen()

    def hasLineStyle(self : "Self | ItemType") -> bool:
        return hasattr(self, "_line_style")

    def lineStyle(self : "Self | ItemType") -> Qt.PenStyle | None:
        return self._line_style if hasattr(self, "_line_style") else None

    def defaultLineStyle(
        self   : "Self | ItemType",
        widget : "QGraphicsView | None" = None
    ) -> Qt.PenStyle | None:
        scene = self._defaultScene(widget)
        key = self._penKeyDefault()
        pen = scene.resources.pen(self.resourcesName(), key)
        return pen.style()

    @checked
    def setLineStyle(self : "Self | ItemType", style: Qt.PenStyle | None | NoChange) -> None:
        if style is NO_CHANGE:
            return
        if not hasattr(self, "_line_style"):
            logger().error("This item does not support line style overrides.")
            return
        self._line_style = style
        self._updatePen()

    # helpers
    def _penKey(self : "Self | ItemType") -> bool:
        return self.isSelected()

    def _penKeyDefault(self : "Self | ItemType") -> bool:
        return False

    def _updatePen(self : "Self | ItemType", _scene : "DrawingScene") -> None:
        raise NotImplementedError("Not wired!")

    @withScene
    def _updatePenFast(self : "Self | ItemType", scene : "DrawingScene") -> None:
        pen = scene.resources.pen(self.resourcesName(), self._penKey())
        self.setPen(pen)

    @withScene
    def _updatePenSlow(self : "Self | ItemType", scene : "DrawingScene") -> None:
        pen = scene.resources.pen(self.resourcesName(), self._penKey())
        override_color = \
            hasattr(self, "_line_color") and not self.isSelected() \
                and self._line_color is not None
        override_width = \
            hasattr(self, "_line_width") and self._line_width is not None
        override_style = \
            hasattr(self, "_line_style") and self._line_style is not None
        if override_color or override_width or override_style:
            pen = QPen(pen)
            if override_color: pen.setColor(self._line_color)
            if override_width: pen.setWidthF(self._line_width)
            if override_style: pen.setStyle(self._line_style)
        self.setPen(pen)
