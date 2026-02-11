from typing import Self, Protocol

from collections.abc import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtGui  import QBrush, QColor

from .....app import logger, settings

from .....core.types import Default, DEFAULT

from ...properties import InherentProperty

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...scenes.drawing import DrawingScene


class ItemProtocol(Protocol):
    def settingsName(self) -> str: ...
    def addSelectionHandler(self, handler: Callable[[bool], None]) -> None: ...
    def brush(self) -> QBrush: ...
    def setBrush(self, brush: QBrush) -> None: ...
    def scene(self) -> "DrawingScene": ...


class ItemFillMixin:
    """Mixin for items that use a brush."""

    # class attributes
    _PROPERTIES_FILL = {
        "Fill Color" : InherentProperty(
            kind    = "Color",
            valid   = lambda self: self.fillColor() is not DEFAULT,
            getter  = lambda self: self.fillColor(),
            setter  = lambda self, value: self.setFillColor(value),
            default = lambda self: self.defaultFillColor()
        ),
        "Fill Style" : InherentProperty(
            kind    = "BrushStyle",
            valid   = lambda self: self.fillStyle() is not DEFAULT,
            getter  = lambda self: self.fillStyle(),
            setter  = lambda self, value: self.setFillStyle(value),
            default = lambda self: self.defaultFillStyle()
        )
    }

    # instance attributes
    _fill_color : QColor        | Default
    _fill_style : Qt.BrushStyle | Default

    def initFill(self : Self | ItemProtocol) -> None:
        if not hasattr(self, "setBrush"):
            logger().error("This item does not support the setBrush method")
        self._fill_color = DEFAULT
        self._fill_style = DEFAULT
        self.fillSettingsChange()
        settings().changed.connect(self.fillSettingsChange)
        self.addSelectionHandler(self.fillSelectionChange)

    def fillSettingsChange(self : Self | ItemProtocol) -> None:
        """Refresh following possible changes to default pen settings."""
        self.setFillColor(self.fillColor())
        self.setFillStyle(self.fillStyle())

    def fillSelectionChange(self : Self | ItemProtocol, selected : bool) -> None:
        scene : "DrawingScene" = self.scene()
        self.setFillColor(scene.selectedFillColor() if selected else self.fillColor())

    def defaultFillColor(self : Self | ItemProtocol) -> QColor:
        return settings().get(f"theme/items/{self.settingsName()}/fill/color")

    def fillColor(self : Self | ItemProtocol) -> QColor | Default:
        return self._fill_color

    def setFillColor(
        self  : Self | ItemProtocol,
        color : QColor | Default
    ) -> None:
        self._fill_color = color
        if color is DEFAULT: color = self.defaultFillColor()
        brush = self.brush()
        brush.setColor(color)
        self.setBrush(brush)

    def defaultFillStyle(self : Self | ItemProtocol) -> Qt.BrushStyle:
        return settings().get(f"theme/items/{self.settingsName()}/fill/style")

    def fillStyle(self : Self | ItemProtocol) -> Qt.BrushStyle | Default:
        return self._fill_style

    def setFillStyle(
        self  : Self | ItemProtocol,
        style : Qt.BrushStyle | Default
    ) -> None:
        self._fill_style = style
        if style is DEFAULT: style = self.defaultFillStyle()
        brush = self.brush()
        brush.setStyle(style)
        self.setBrush(brush)
