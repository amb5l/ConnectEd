from typing import Self
from types  import SimpleNamespace

from PyQt6.QtCore import Qt
from PyQt6.QtGui  import QBrush, QColor

from .....app import settings

from ...property import PropertySpec

from .. import Default, DEFAULT, NO_CHANGE, Appearance, FillPref, FillPrefChange

from .           import ItemMixin


class Fill:
    _parent   : "ItemMixin"
    _color    : Default | QColor
    _style    : Default | Qt.BrushStyle
    _normal   : QBrush
    _selected : QBrush
    _brush    : QBrush

    def __init__(
        self   : Self,
        parent : "ItemMixin",
        pref   : FillPref = FillPref(DEFAULT, DEFAULT)
    ) -> None:
        self._parent   = parent
        self._color    = pref.color
        self._style    = pref.style
        self._normal   = QBrush()
        self._selected = QBrush()
        self.onSettingsChange()

    def getColor(self : Self) -> Default | QColor:
        return self._color

    def setColor(self : Self, color : Default | QColor) -> None:
        self._color = color
        self.onSettingsChange()

    def getStyle(self : Self) -> Default | Qt.BrushStyle:
        return self._style

    def setStyle(self : Self, style : Default | Qt.BrushStyle) -> None:
        self._style = style
        self.onSettingsChange()

    def getPref(self : Self) -> FillPref:
        return FillPref(self._color, self._style)

    def setPref(self : Self, c : FillPref | FillPrefChange) -> None:
        if c.color is not NO_CHANGE: self._color = c.color
        if c.style is not NO_CHANGE: self._style = c.style
        self.onSettingsChange()

    def getDefaults(self : Self) -> SimpleNamespace:
        return settings().get(f"theme/items/{self._parent.settingsName()}/fill")

    def onSettingsChange(self : Self) -> None:
        default = self.getDefaults()
        color_normal = default.color if self._color is DEFAULT else self._color
        color_normal.setAlpha(settings().get("display/alpha"))
        color_selected = settings().get("theme/selected/fill")
        color_selected.setAlpha(settings().get("display/alpha"))
        style = default.style if self._style is DEFAULT else self._style
        self._normal.setColor(color_normal)
        self._normal.setStyle(style)
        self._selected.setColor(color_selected)
        self._selected.setStyle(style)
        self.onSelectionChange(self._parent.isSelected())

    def onSelectionChange(self : Self, selected : bool) -> None:
        self._brush = self._selected if selected else self._normal
        if hasattr(self._parent, "setBrush"):
            self._parent.setBrush(self._brush)


class ItemFillMixin:
    _PROPERTY_SPECS_FILL = {
        "Fill Color" : PropertySpec(
            kind    = "QColor",
            valid   = lambda self: self.a.fill is not None and self.a.fill.getColor() is not DEFAULT,
            getter  = lambda self: self.a.fill.getColor(),
            setter  = lambda self, value: self.a.fill.setColor(value),
            default = lambda self: self.a.fill.getDefaults().color
        ),
        "Fill Style" : PropertySpec(
            kind    = "BrushStyle",
            valid   = lambda self: self.a.fill is not None and self.a.fill.getStyle() is not DEFAULT,
            getter  = lambda self: self.a.fill.getStyle(),
            setter  = lambda self, value: self.a.fill.setStyle(value),
            default = lambda self: self.a.fill.getDefaults().style
        )
    }

    a : Appearance

    def initFill(self : Self):
        if not hasattr(self, "a"):
            self.a = Appearance()
        self.a.fill = Fill(self)
