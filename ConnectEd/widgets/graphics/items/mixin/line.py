from typing import Self, Protocol

from collections.abc import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtGui  import QPen, QColor

from .....app import logger, settings

from .....core.types import DataKind, Default, DEFAULT, Color

from ...properties import InherentProperty

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...scenes.drawing import DrawingScene


class ItemProtocol(Protocol):
    def settingsName(self) -> str: ...
    def addSelectionHandler(self, handler: Callable[[bool], None]) -> None: ...
    def pen(self) -> QPen: ...
    def setPen(self, pen: QPen) -> None: ...
    def scene(self) -> "DrawingScene": ...
    def isSelected(self) -> bool: ...


class ItemLineMixin:
    """
    Mixin for items that use a pen.
    """

    # class attributes
    _PROPERTIES_LINE = {
        "Line Color" : InherentProperty(
            kind    = DataKind.COLOR,
            worthy  = lambda self: self.lineColor() != DEFAULT,
            getter  = lambda self: self.lineColor(),
            setter  = lambda self, value: self.setLineColor(value),
            default = lambda self: self.defaultLineColor()
        ),
        "Line Width" : InherentProperty(
            kind    = DataKind.PEN_WIDTH,
            worthy  = lambda self: self.lineWidth() != DEFAULT,
            getter  = lambda self: self.lineWidth(),
            setter  = lambda self, value: self.setLineWidth(value),
            default = lambda self: self.defaultLineWidth()
        ),
        "Line Style" : InherentProperty(
            kind    = DataKind.PEN_STYLE,
            worthy  = lambda self: self.lineStyle() != DEFAULT,
            getter  = lambda self: self.lineStyle(),
            setter  = lambda self, value: self.setLineStyle(value),
            default = lambda self: self.defaultLineStyle()
        )
    }

    # instance attributes
    _line_color : QColor      | Default
    _line_width : float       | Default
    _line_style : Qt.PenStyle | Default

    def initLine(self : Self | ItemProtocol) -> None:
        if not hasattr(self, "setPen"):
            logger().error("This item does not support the setPen method")
        self._line_color = DEFAULT
        self._line_width = DEFAULT
        self._line_style = DEFAULT
        self.lineSettingsChange()
        settings().changed.connect(self.lineSettingsChange)
        self.addSelectionHandler(self.lineSelectionChange)

    def lineSettingsChange(self : Self | ItemProtocol) -> None:
        """Refresh following possible changes to default pen settings."""
        self.setLineColor(self.lineColor())
        self.setLineWidth(self.lineWidth())
        self.setLineStyle(self.lineStyle())

    def lineSelectionChange(self : Self | ItemProtocol, selected : bool) -> None:
        self.setLineColor(selected=selected)

    def defaultLineColor(self : Self | ItemProtocol) -> QColor:
        return settings().get(f"theme/items/{self.settingsName()}/line/color")

    def lineColor(self : Self | ItemProtocol) -> Color:
        return self._line_color

    def setLineColor(
        self     : Self | ItemProtocol,
        color    : Color | None = None,
        selected : bool  | None = None
    ) -> None:
        if color is not None:
            self._line_color = color
        else:
            color = self._line_color
        if color == DEFAULT:
            color = self.defaultLineColor()
        if selected is None:
            selected = self.isSelected()
        if selected:
            scene : "DrawingScene" = self.scene()
            color = scene.selectedLineColor()
        pen = self.pen()
        pen.setColor(color)
        self.setPen(pen)

    def defaultLineWidth(self : Self | ItemProtocol) -> float:
        return settings().get(f"theme/items/{self.settingsName()}/line/width")

    def lineWidth(self : Self | ItemProtocol) -> float | Default:
        return self._line_width

    def setLineWidth(
        self  : Self | ItemProtocol,
        width : float | Default
    ) -> None:
        self._line_width = width
        if width == DEFAULT: width = self.defaultLineWidth()
        pen = self.pen()
        pen.setWidthF(width)
        self.setPen(pen)

    def defaultLineStyle(self : Self | ItemProtocol) -> Qt.PenStyle:
        return settings().get(f"theme/items/{self.settingsName()}/line/style")

    def lineStyle(self : Self | ItemProtocol) -> Qt.PenStyle | Default:
        return self._line_style

    def setLineStyle(
        self  : Self | ItemProtocol,
        style : Qt.PenStyle | Default
    ) -> None:
        self._line_style = style
        if style == DEFAULT: style = self.defaultLineStyle()
        pen = self.pen()
        pen.setStyle(style)
        self.setPen(pen)
