from __future__ import annotations

from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtGui     import QColor, QBrush

from ......app import logger

from ......core.check import checked
from ......core.types import NoChange

from ....properties import PropertiesManager, PropertiesMixin

from ....scenes import withScene

from ...protocols import SetBrushProtocol

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....views.diagram  import DiagramView
    from ....scenes.diagram import DiagramScene


class ItemPresentationFillMixin:

    # instance attributes
    _fill_color : QColor        | None
    _fill_style : Qt.BrushStyle | None

    # external instance attributes
    properties : PropertiesManager  # provided by PropertiesMixin

    # API

    def hasFill(self : Self) -> bool:
        return self.hasFillColor() or self.hasFillStyle()

    def hasFillColor(self : Self) -> bool:
        return hasattr(self, "_fill_color")

    def fillColor(self : Self) -> QColor | None:
        return self._fill_color if hasattr(self, "_fill_color") else None

    def defaultFillColor(
        self : Self,
        view : DiagramView | None = None
    ) -> QColor | None:
        from .. import ItemNamesMixin
        from . import ItemPresentationMixin
        if not isinstance(self, ItemPresentationMixin) \
        or not isinstance(self, ItemNamesMixin):
            raise TypeError("Bad host")
        if (scene := self._defaultScene(view)) is None:
            return None
        key = self._resourceKeyDefault()
        brush = scene.resources.brush(self.resourcesName(), key)
        return brush.color()

    @checked
    def setFillColor(self : Self, color: QColor | None | NoChange) -> None:
        if isinstance(color, NoChange):
            return
        if not hasattr(self, "_fill_color"):
            logger().error("This item does not support fill color overrides.")
            return
        self._fill_color = color
        self._updateBrush()
        if isinstance(self, PropertiesMixin):
            self.properties.signalChanges("Fill Color")

    def hasFillStyle(self : Self) -> bool:
        return hasattr(self, "_fill_style")

    def fillStyle(self : Self) -> Qt.BrushStyle | None:
        return self._fill_style if hasattr(self, "_fill_style") else None

    def defaultFillStyle(
        self : Self,
        view : DiagramView | None = None
    ) -> Qt.BrushStyle | None:
        from .. import ItemNamesMixin
        from . import ItemPresentationMixin
        if not isinstance(self, ItemPresentationMixin) \
        or not isinstance(self, ItemNamesMixin):
            raise TypeError("Bad host")
        if (scene := self._defaultScene(view)) is None:
            return None
        key = self._resourceKeyDefault()
        brush = scene.resources.brush(self.resourcesName(), key)
        return brush.style()

    @checked
    def setFillStyle(
        self  : Self,
        style : Qt.BrushStyle | None | NoChange
        ) -> None:
        if isinstance(style, NoChange):
            return
        if not hasattr(self, "_fill_style"):
            logger().error("This item does not support fill style overrides.")
            return
        self._fill_style = style
        self._updateBrush()
        if isinstance(self, PropertiesMixin):
            self.properties.signalChanges("Fill Style")

    # helpers

    def _updateBrush(self : Self, _scene : DiagramScene | None = None) -> None:
        raise NotImplementedError("Not wired!")

    @withScene
    def _updateBrushFast(
        self : Self,
        scene : DiagramScene
    ) -> None:
        from .. import ItemNamesMixin
        from . import ItemPresentationMixin
        if not isinstance(self, SetBrushProtocol) \
        or not isinstance(self, ItemNamesMixin) \
        or not isinstance(self, ItemPresentationMixin):
            raise TypeError("Bad host")
        brush = scene.resources.brush(self.resourcesName(), self._resourceKey())
        self.setBrush(brush)

    @withScene
    def _updateBrushSlow(
        self  : Self,
        scene : DiagramScene
    ) -> None:
        from .. import ItemNamesMixin
        from . import ItemPresentationMixin
        if not isinstance(self, QGraphicsItem) \
        or not isinstance(self, SetBrushProtocol) \
        or not isinstance(self, ItemNamesMixin) \
        or not isinstance(self, ItemPresentationMixin):
            raise TypeError("Bad host")
        brush = scene.resources.brush(self.resourcesName(), self._resourceKey())
        unselected = not self.isSelected()
        override_color = self._fill_color if unselected \
            and hasattr(self, "_fill_color") and self._fill_color is not None \
            else None
        override_style = self._fill_style if unselected \
            and hasattr(self, "_fill_style") and self._fill_style is not None \
            else None
        if override_color or override_style:
            brush = QBrush(brush)
            if override_color is not None: brush.setColor(override_color)
            if override_style is not None: brush.setStyle(override_style)
        self.setBrush(brush)
