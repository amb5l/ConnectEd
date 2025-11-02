from typing import Self
from types  import SimpleNamespace

from PyQt6.QtCore import Qt
from PyQt6.QtGui  import QPen, QColor

from .....app import settings

from ...properties import PropertySpec

from .. import Default, DEFAULT, NO_CHANGE, Appearance, LinePref, LinePrefChange

from . import ItemMixin


class Line:
    # class attributes
    _CAP_STYLE  = Qt.PenCapStyle.RoundCap
    _JOIN_STYLE = Qt.PenJoinStyle.RoundJoin

    # instance attributes
    parent   : "ItemMixin"
    color    : Default | QColor
    width    : Default | float
    style    : Default | Qt.PenStyle
    normal   : QPen
    selected : QPen
    pen      : QPen

    def __init__(
        self   : Self,
        parent : "ItemMixin",
        pref   : LinePref = LinePref(DEFAULT, DEFAULT, DEFAULT)
    ) -> None:
        self.parent = parent
        self.color  = pref.color
        self.width  = pref.width
        self.style  = pref.style
        self.normal = QPen()
        self.normal.setCapStyle(self._CAP_STYLE)
        self.normal.setJoinStyle(self._JOIN_STYLE)
        self.selected = QPen()
        self.selected.setCapStyle(self._CAP_STYLE)
        self.selected.setJoinStyle(self._JOIN_STYLE)
        self.onSettingsChange()

    def getColor(self : Self) -> Default | QColor:
        return self.color

    def setColor(self : Self, color : Default | QColor) -> None:
        self.color = color
        self.onSettingsChange()

    def getWidth(self : Self) -> Default | float:
        return self.width

    def setWidth(self : Self, width : Default | float) -> None:
        self.width = width
        self.onSettingsChange()

    def getStyle(self : Self) -> Default | Qt.PenStyle:
        return self.style

    def setStyle(self : Self, style : Default | Qt.PenStyle) -> None:
        self.style = style
        self.onSettingsChange()

    def getPref(self : Self) -> LinePref:
        return LinePref(self.color, self.width, self.style)

    def setPref(self : Self, c : LinePref | LinePrefChange) -> None:
        if c.color is not NO_CHANGE: self.color = c.color
        if c.width is not NO_CHANGE: self.width = c.width
        if c.style is not NO_CHANGE: self.style = c.style
        self.onSettingsChange()

    def getDefaults(self : Self) -> SimpleNamespace:
        settings_name = self.parent.__class__.__name__
        return settings().get(f"theme/items/{settings_name}/line")

    def onSettingsChange(self : Self) -> None:
        default = self.getDefaults()
        color_normal = default.color if self.color is DEFAULT else self.color
        color_normal.setAlpha(settings().get("display/alpha"))
        color_selected = settings().get("theme/selected/line")
        color_selected.setAlpha(settings().get("display/alpha"))
        width = default.width if self.width is DEFAULT else self.width
        style = default.style if self.style is DEFAULT else self.style
        self.normal.setColor(color_normal)
        self.normal.setWidthF(width)
        self.normal.setStyle(style)
        self.selected.setColor(color_selected)
        self.selected.setWidthF(width)
        self.selected.setStyle(style)
        self.onSelectionChange(self.parent.isSelected())

    def onSelectionChange(self : Self, selected : bool) -> None:
        self.pen = self.selected if selected else self.normal
        if hasattr(self.parent, "setPen"):
            self.parent.setPen(self.pen)


class ItemLineMixin:
    _PROPERTY_SPECS_LINE = {
        "Line Color" : PropertySpec(
            type_name = "QColor",
            exists    = lambda self: self.a.line is not None,
            getter    = lambda self: self.a.line.getColor(),
            setter    = lambda self, value: self.a.line.setColor(value),
            default   = lambda self: self.a.line.getDefaults().color
        ),
        "Line Width" : PropertySpec(
            type_name = "float",
            exists    = lambda self: self.a.line is not None,
            getter    = lambda self: self.a.line.getWidth(),
            setter    = lambda self, value: self.a.line.setWidth(value),
            default   = lambda self: self.a.line.getDefaults().width
        ),
        "Line Style" : PropertySpec(
            type_name = "PenStyle",
            exists    = lambda self: self.a.line is not None,
            getter    = lambda self: self.a.line.getStyle(),
            setter    = lambda self, value: self.a.line.setStyle(value),
            default   = lambda self: self.a.line.getDefaults().style
        )
    }

    a : Appearance

    def initLine(self : Self):
        if not hasattr(self, "a"):
            self.a = Appearance()
        self.a.line = Line(self)
