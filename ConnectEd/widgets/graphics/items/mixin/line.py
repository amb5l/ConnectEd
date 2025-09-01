from typing import Self

from PyQt6.QtCore import Qt

from ...properties import PropertySpec

from .. import Line


class ElementLineMixin:
    _CAP_STYLE  = Qt.PenCapStyle.SquareCap
    _JOIN_STYLE = Qt.PenJoinStyle.MiterJoin
    _PROPERTY_SPECS_LINE = {
        "Line Color" : PropertySpec(
            type_name = "QColor",
            exists    = lambda self: self.line is not None,
            getter    = lambda self: self.line.getColor(),
            setter    = lambda self, value: self.line.setColor(value),
            default   = lambda self: self.line.getDefaults().color
        ),
        "Line Width" : PropertySpec(
            type_name = "float",
            exists    = lambda self: self.line is not None,
            getter    = lambda self: self.line.getWidth(),
            setter    = lambda self, value: self.line.setWidth(value),
            default   = lambda self: self.line.getDefaults().width
        ),
        "Line Style" : PropertySpec(
            type_name = "PenStyle",
            exists    = lambda self: self.line is not None,
            getter    = lambda self: self.line.getStyle(),
            setter    = lambda self, value: self.line.setStyle(value),
            default   = lambda self: self.line.getDefaults().style
        )
    }

    line : Line

    def initLine(self : Self):
        self.line = Line(self)
