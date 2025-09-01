from typing import Self

from ...properties import PropertySpec

from .. import Fill


class ElementFillMixin:
    _PROPERTY_SPECS_FILL = {
        "Fill Color" : PropertySpec(
            type_name = "QColor",
            exists    = lambda self: self.fill is not None,
            getter    = lambda self: self.fill.getColor(),
            setter    = lambda self, value: self.fill.setColor(value),
            default   = lambda self: self.fill.getDefaults().color
        ),
        "Fill Style" : PropertySpec(
            type_name = "BrushStyle",
            exists    = lambda self: self.fill is not None,
            getter    = lambda self: self.fill.getStyle(),
            setter    = lambda self, value: self.fill.setStyle(value),
            default   = lambda self: self.fill.getDefaults().style
        )
    }

    fill : Fill

    def initFill(self : Self):
        self.fill = Fill(self)
