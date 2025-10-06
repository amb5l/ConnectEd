from typing import Self
from types  import SimpleNamespace

from PyQt6.QtCore import Qt
from PyQt6.QtGui  import QBrush, QColor

from .....app import settings

from ...properties import PropertySpec

from .. import Default, DEFAULT, NO_CHANGE, Appearance, FillPref, FillPrefChange

from . import ElementMixin


class Fill:
    parent   : "ElementMixin"
    color    : Default | QColor
    style    : Default | Qt.BrushStyle
    normal   : QBrush
    selected : QBrush
    brush    : QBrush

    def __init__(
        self   : Self,
        parent : "ElementMixin",
        pref   : FillPref = FillPref(DEFAULT, DEFAULT)
    ) -> None:
        self.parent   = parent
        self.color    = pref.color
        self.style    = pref.style
        self.normal   = QBrush()
        self.selected = QBrush()
        self.onSettingsChange()

    def getColor(self : Self) -> Default | QColor:
        return self.color

    def setColor(self : Self, color : Default | QColor) -> None:
        self.color = color
        self.onSettingsChange()

    def getStyle(self : Self) -> Default | Qt.BrushStyle:
        return self.style

    def setStyle(self : Self, style : Default | Qt.BrushStyle) -> None:
        self.style = style
        self.onSettingsChange()

    def getPref(self : Self) -> FillPref:
        return FillPref(self.color, self.style)

    def setPref(self : Self, c : FillPref | FillPrefChange) -> None:
        if c.color is not NO_CHANGE: self.color = c.color
        if c.style is not NO_CHANGE: self.style = c.style
        self.onSettingsChange()

    def getDefaults(self : Self) -> SimpleNamespace:
        settings_name = self.parent.__class__.__name__
        return settings().get(f"theme/elements/{settings_name}/fill")

    def onSettingsChange(self : Self) -> None:
        default = self.getDefaults()
        color_normal = default.color if self.color is DEFAULT else self.color
        color_normal.setAlpha(settings().get("display/alpha"))
        color_selected = settings().get("theme/selected/fill")
        color_selected.setAlpha(settings().get("display/alpha"))
        style = default.style if self.style is DEFAULT else self.style
        self.normal.setColor(color_normal)
        self.normal.setStyle(style)
        self.selected.setColor(color_selected)
        self.selected.setStyle(style)
        self.onSelectionChange(self.parent.isSelected())

    def onSelectionChange(self : Self, selected : bool) -> None:
        self.brush = self.selected if selected else self.normal
        if hasattr(self.parent, "setBrush"):
            self.parent.setBrush(self.brush)


class ElementFillMixin:
    _PROPERTY_SPECS_FILL = {
        "Fill Color" : PropertySpec(
            type_name = "QColor",
            exists    = lambda self: self.a.fill is not None,
            getter    = lambda self: self.a.fill.getColor(),
            setter    = lambda self, value: self.a.fill.setColor(value),
            default   = lambda self: self.a.fill.getDefaults().color
        ),
        "Fill Style" : PropertySpec(
            type_name = "BrushStyle",
            exists    = lambda self: self.a.fill is not None,
            getter    = lambda self: self.a.fill.getStyle(),
            setter    = lambda self, value: self.a.fill.setStyle(value),
            default   = lambda self: self.a.fill.getDefaults().style
        )
    }

    a : Appearance

    def initFill(self : Self):
        if not hasattr(self, "a"):
            self.a = Appearance()
        self.a.fill = Fill(self)
