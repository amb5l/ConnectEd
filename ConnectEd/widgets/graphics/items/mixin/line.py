from typing import Self, Protocol

from collections.abc import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtGui  import QPen, QColor

from .....app import logger, settings

from ...properties import PropertySpec

from .. import Default, DEFAULT

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...scenes.drawing import DrawingScene


class ItemProtocol(Protocol):
    def settingsName(self) -> str: ...
    def addSelectionHandler(self, handler: Callable[[bool], None]) -> None: ...
    def pen(self) -> QPen: ...
    def setPen(self, pen: QPen) -> None: ...
    def scene(self) -> "DrawingScene": ...


class ItemLineMixin:
    """
    Mixin for items that use a pen.
    """

    # class attributes
    _PROPERTIES_LINE = {
        "Line Color" : PropertySpec(
            type_name = "QColor",
            valid     = lambda self: self.lineColor() is not DEFAULT,
            getter    = lambda self: self.lineColor(),
            setter    = lambda self, value: self.setLineColor(value),
            default   = lambda self: self.defaultLineColor()
        ),
        "Line Width" : PropertySpec(
            type_name = "LineWidth",  # a "subtype" of float - see str2val
            valid     = lambda self: self.lineWidth() is not DEFAULT,
            getter    = lambda self: self.lineWidth(),
            setter    = lambda self, value: self.setLineWidth(value),
            default   = lambda self: self.defaultLineWidth()
        ),
        "Line Style" : PropertySpec(
            type_name = "PenStyle",
            valid     = lambda self: self.lineStyle() is not DEFAULT,
            getter    = lambda self: self.lineStyle(),
            setter    = lambda self, value: self.setLineStyle(value),
            default   = lambda self: self.defaultLineStyle()
        )
    }

    # instance attributes
    _pen_color : QColor      | Default
    _pen_width : float       | Default
    _pen_style : Qt.PenStyle | Default

    def initLine(self : Self | ItemProtocol) -> None:
        if not hasattr(self, "setPen"):
            logger().error("This item does not support the setPen method")
        self._pen_color = DEFAULT
        self._pen_width = DEFAULT
        self._pen_style = DEFAULT
        self.lineSettingsChange()
        settings().changed.connect(self.lineSettingsChange)
        self.addSelectionHandler(self.lineSelectionChange)

    def lineSettingsChange(self : Self | ItemProtocol) -> None:
        """Refresh following possible changes to default pen settings."""
        self.setLineColor(self.lineColor())
        self.setLineWidth(self.lineWidth())
        self.setLineStyle(self.lineStyle())

    def lineSelectionChange(self : Self | ItemProtocol, selected : bool) -> None:
        scene : "DrawingScene" = self.scene()
        self.setLineColor(scene.selectedLineColor() if selected else self.lineColor())

    def defaultLineColor(self : Self | ItemProtocol) -> QColor | Default:
        return settings().get(f"theme/items/{self.settingsName()}/line/color")

    def lineColor(self : Self | ItemProtocol) -> QColor | Default:
        return self._pen_color

    def setLineColor(
        self : Self | ItemProtocol,
        color : QColor | Default
    ) -> None:
        if color is DEFAULT: color = self.defaultLineColor()
        pen = self.pen()
        pen.setColor(color)
        self.setPen(pen)

    def defaultLineWidth(self : Self | ItemProtocol) -> float | Default:
        return settings().get(f"theme/items/{self.settingsName()}/line/width")

    def lineWidth(self : Self | ItemProtocol) -> float | Default:
        return self._pen_width

    def setLineWidth(
        self  : Self | ItemProtocol,
        width : float | Default
    ) -> None:
        if width is DEFAULT: width = self.defaultLineWidth()
        pen = self.pen()
        pen.setWidthF(width)
        self.setPen(pen)

    def defaultLineStyle(self : Self | ItemProtocol) -> Qt.PenStyle | Default:
        return settings().get(f"theme/items/{self.settingsName()}/line/style")

    def lineStyle(self : Self | ItemProtocol) -> Qt.PenStyle | Default:
        return self._pen_style

    def setLineStyle(
        self  : Self | ItemProtocol,
        style : Qt.PenStyle | Default
    ) -> None:
        if style is DEFAULT: style = self.defaultLineStyle()
        pen = self.pen()
        pen.setStyle(style)
        self.setPen(pen)
