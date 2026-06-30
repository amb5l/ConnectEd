from __future__ import annotations

from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtGui     import QPen, QColor

from ......app import logger

from ......core.check import checked
from ......core.types import NoChange

from ....scenes import withScene

from ....properties import PropertiesManager, PropertiesMixin

from ...protocols import SetPenProtocol

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....views.diagram  import DiagramView
    from ....scenes.diagram import DiagramScene


class ItemPresentationLineMixin:

    # instance attributes
    _line_color : QColor      | None
    _line_width : float       | None
    _line_style : Qt.PenStyle | None

    # external instance attributes
    properties : PropertiesManager  # provided by PropertiesMixin

    # API

    def hasLine(self : Self) -> bool:
        return self.hasLineColor() or self.hasLineWidth() or self.hasLineStyle()

    def hasLineColor(self : Self) -> bool:
        return hasattr(self, "_line_color")

    def defaultLineColor(
        self : Self,
        view : DiagramView | None = None
    ) -> QColor | None:
        from .. import ItemNamesMixin
        from . import ItemPresentationMixin
        if not isinstance(self, ItemPresentationMixin) \
        or not isinstance(self, ItemNamesMixin):
            raise TypeError("Bad host")
        scene = self._defaultScene(view)
        if scene is None:
            return None
        key = self._resourceKeyDefault()
        pen = scene.resources.pen(self.resourcesName(), key)
        return pen.color()

    def lineColor(self : Self) -> QColor | None:
        return self._line_color if hasattr(self, "_line_color") else None

    @checked
    def setLineColor(self : Self, color: QColor | None | NoChange) -> None:
        if isinstance(color, NoChange):
            return
        if not hasattr(self, "_line_color"):
            logger().error("This item does not support line color overrides.")
            return
        self._line_color = color
        self._updatePen()
        if isinstance(self, PropertiesMixin):
            self.properties.signalChanges("Line Color")

    def hasLineWidth(self : Self) -> bool:
        return hasattr(self, "_line_width")

    def lineWidth(self : Self) -> float | None:
        return self._line_width if hasattr(self, "_line_width") else None

    def defaultLineWidth(
        self : Self,
        view : DiagramView | None = None
    ) -> float | None:
        from .. import ItemNamesMixin
        from . import ItemPresentationMixin
        if not isinstance(self, ItemPresentationMixin) \
        or not isinstance(self, ItemNamesMixin):
            raise TypeError("Bad host")
        scene = self._defaultScene(view)
        key = self._resourceKeyDefault()
        if scene is None:
            return None
        pen = scene.resources.pen(self.resourcesName(), key)
        return pen.widthF()

    @checked
    def setLineWidth(self : Self, width: float | None | NoChange) -> None:
        if isinstance(width, NoChange):
            return
        if not hasattr(self, "_line_width"):
            logger().error("This item does not support line width overrides.")
            return
        self._line_width = width
        self._updatePen()
        if isinstance(self, PropertiesMixin):
            self.properties.signalChanges("Line Width")

    def hasLineStyle(self : Self) -> bool:
        return hasattr(self, "_line_style")

    def lineStyle(self : Self) -> Qt.PenStyle | None:
        return self._line_style if hasattr(self, "_line_style") else None

    def defaultLineStyle(
        self : Self,
        view : DiagramView | None = None
    ) -> Qt.PenStyle | None:
        from .. import ItemNamesMixin
        from . import ItemPresentationMixin
        if not isinstance(self, ItemPresentationMixin) \
        or not isinstance(self, ItemNamesMixin):
            raise TypeError("Bad host")
        scene = self._defaultScene(view)
        if scene is None:
            return None
        key = self._resourceKeyDefault()
        pen = scene.resources.pen(self.resourcesName(), key)
        return pen.style()

    @checked
    def setLineStyle(
        self  : Self,
        style : Qt.PenStyle | None | NoChange
    ) -> None:
        from .. import ItemNamesMixin
        from . import ItemPresentationMixin
        if not isinstance(self, ItemPresentationMixin) \
        or not isinstance(self, ItemNamesMixin):
            raise TypeError("Bad host")
        if isinstance(style, NoChange):
            return
        if not hasattr(self, "_line_style"):
            logger().error("This item does not support line style overrides.")
            return
        self._line_style = style
        self._updatePen()
        if isinstance(self, PropertiesMixin):
            self.properties.signalChanges("Line Style")

    # helpers

    def _updatePen(self : Self, _scene : DiagramScene | None = None) -> None:
        raise NotImplementedError("Not wired!")

    @withScene
    def _updatePenFast(self : Self, scene : DiagramScene) -> None:
        from .. import ItemNamesMixin
        from . import ItemPresentationMixin
        if not isinstance(self, SetPenProtocol) \
        or not isinstance(self, ItemNamesMixin) \
        or not isinstance(self, ItemPresentationMixin):
            raise TypeError("Bad host")
        pen = scene.resources.pen(self.resourcesName(), self._resourceKey())
        self.setPen(pen)

    @withScene
    def _updatePenSlow(self : Self, scene : DiagramScene) -> None:
        from .. import ItemNamesMixin
        from . import ItemPresentationMixin
        if not isinstance(self, QGraphicsItem) \
        or not isinstance(self, SetPenProtocol) \
        or not isinstance(self, ItemNamesMixin) \
        or not isinstance(self, ItemPresentationMixin):
            raise TypeError("Bad host")
        pen = scene.resources.pen(self.resourcesName(), self._resourceKey())
        unselected = not self.isSelected()
        override_color = self._line_color if unselected \
            and hasattr(self, "_line_color") and self._line_color is not None \
            else None
        override_width = self._line_width if unselected \
            and hasattr(self, "_line_width") and self._line_width is not None \
            else None
        override_style = self._line_style if unselected \
            and hasattr(self, "_line_style") and self._line_style is not None \
            else None
        if override_color or override_width or override_style:
            pen = QPen(pen)
            if override_color is not None: pen.setColor(override_color)
            if override_width is not None: pen.setWidthF(override_width)
            if override_style is not None: pen.setStyle(override_style)
        self.setPen(pen)
