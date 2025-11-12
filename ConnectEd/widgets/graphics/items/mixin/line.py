from typing import Self
from types  import SimpleNamespace

from PyQt6.QtCore import Qt
from PyQt6.QtGui  import QPen, QColor

from .....app import settings

from ...property import PropertySpec

from .. import Default, DEFAULT, NO_CHANGE, Appearance, LinePref, LinePrefChange

from .           import ItemMixin


class Line:
    # class attributes
    _CAP_STYLE  = Qt.PenCapStyle.RoundCap
    _JOIN_STYLE = Qt.PenJoinStyle.RoundJoin

    # instance attributes
    _parent   : "ItemMixin"
    _color    : Default | QColor
    _width    : Default | float
    _style    : Default | Qt.PenStyle
    _normal   : QPen
    _selected : QPen
    _pen      : QPen

    def __init__(
        self   : Self,
        parent : "ItemMixin",
        pref   : LinePref = LinePref(DEFAULT, DEFAULT, DEFAULT)
    ) -> None:
        self._parent = parent
        self._color  = pref.color
        self._width  = pref.width
        self._style  = pref.style
        self._normal = QPen()
        self._normal.setCapStyle(self._CAP_STYLE)
        self._normal.setJoinStyle(self._JOIN_STYLE)
        self._selected = QPen()
        self._selected.setCapStyle(self._CAP_STYLE)
        self._selected.setJoinStyle(self._JOIN_STYLE)
        self.onSettingsChange()

    def getColor(self : Self) -> Default | QColor:
        return self._color

    def setColor(self : Self, color : Default | QColor) -> None:
        self._color = color
        self.onSettingsChange()

    def getWidth(self : Self) -> Default | float:
        return self._width

    def setWidth(self : Self, width : Default | float) -> None:
        self._width = width
        self.onSettingsChange()

    def getStyle(self : Self) -> Default | Qt.PenStyle:
        return self._style

    def setStyle(self : Self, style : Default | Qt.PenStyle) -> None:
        self._style = style
        self.onSettingsChange()

    def getPref(self : Self) -> LinePref:
        return LinePref(self._color, self._width, self._style)

    def setPref(self : Self, c : LinePref | LinePrefChange) -> None:
        if c.color is not NO_CHANGE: self._color = c.color
        if c.width is not NO_CHANGE: self._width = c.width
        if c.style is not NO_CHANGE: self._style = c.style
        self.onSettingsChange()

    def getDefaults(self : Self) -> SimpleNamespace:
        return settings().get(f"theme/items/{self._parent.settingsName()}/line")

    def onSettingsChange(self : Self) -> None:
        default = self.getDefaults()
        color_normal = default.color if self._color is DEFAULT else self._color
        color_normal.setAlpha(settings().get("display/alpha"))
        color_selected = settings().get("theme/selected/line")
        color_selected.setAlpha(settings().get("display/alpha"))
        width = default.width if self._width is DEFAULT else self._width
        style = default.style if self._style is DEFAULT else self._style
        self._normal.setColor(color_normal)
        self._normal.setWidthF(width)
        self._normal.setStyle(style)
        self._selected.setColor(color_selected)
        self._selected.setWidthF(width)
        self._selected.setStyle(style)
        self.onSelectionChange(self._parent.isSelected())

    def onSelectionChange(self : Self, selected : bool) -> None:
        self._pen = self._selected if selected else self._normal
        if hasattr(self._parent, "setPen"):
            self._parent.setPen(self._pen)


class ItemLineMixin:
    _PROPERTY_SPECS_LINE = {
        "Line Color" : PropertySpec(
            type_name = "QColor",
            valid     = lambda self: self.a.line is not None,
            getter    = lambda self: self.a.line.getColor(),
            setter    = lambda self, value: self.a.line.setColor(value),
            default   = lambda self: self.a.line.getDefaults().color
        ),
        "Line Width" : PropertySpec(
            type_name = "LineWidth",  # a "subtype" of float - see str2val
            valid     = lambda self: self.a.line is not None,
            getter    = lambda self: self.a.line.getWidth(),
            setter    = lambda self, value: self.a.line.setWidth(value),
            default   = lambda self: self.a.line.getDefaults().width
        ),
        "Line Style" : PropertySpec(
            type_name = "PenStyle",
            valid     = lambda self: self.a.line is not None,
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
