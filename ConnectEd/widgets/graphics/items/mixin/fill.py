from typing import Self, Protocol

from collections.abc import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtGui  import QBrush, QColor

from .....app import logger, settings

from .....core.types import DataKind, Default, DEFAULT, Color

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
    def isSelected(self) -> bool: ...


class ItemFillMixin:
    """Mixin for items that use a brush."""

    # class attributes
    _PROPERTIES_FILL = {
        "Fill Color" : InherentProperty(
            kind    = DataKind.COLOR,
            worthy   = lambda self: self.fillColor() is not DEFAULT,
            getter  = lambda self: self.fillColor(),
            setter  = lambda self, value: self.setFillColor(value),
            default = lambda self: self.defaultFillColor()
        ),
        "Fill Style" : InherentProperty(
            kind    = DataKind.BRUSH_STYLE,
            worthy   = lambda self: self.fillStyle() is not DEFAULT,
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
        self.setFillColor(selected=selected)

    def defaultFillColor(self : Self | ItemProtocol) -> QColor:
        return settings().get(f"theme/items/{self.settingsName()}/fill/color")

    def fillColor(self : Self | ItemProtocol) -> Color | Default:
        return self._fill_color

    def setFillColor(
        self     : Self | ItemProtocol,
        color    : Color | None = None,
        selected : bool  | None = None
    ) -> None:
        if color is not None:
            self._fill_color = color
        else:
            color = self._fill_color
        if color is DEFAULT:
            color = self.defaultFillColor()
        if selected is None:
            selected = self.isSelected()
        if selected:
            scene : "DrawingScene" = self.scene()
            color = scene.selectedFillColor()
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
