from typing import Self
from types  import SimpleNamespace

from PyQt6.QtCore import Qt, QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtGui  import QBrush, QColor

from .....core.utils import val2str, str2val

from ...properties import PropertySpec

from .. import Default, DEFAULT, NO_CHANGE, FillPref, FillPrefChange

from . import ElementMixin

from ..... import hub


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
        return hub.settings.getTheme(f"elements/{settings_name}/fill")

    def onSettingsChange(self : Self) -> None:
        default = self.getDefaults()
        color_normal = default.color if self.color is DEFAULT else self.color
        color_normal.setAlpha(hub.settings.get("display/alpha"))
        color_selected = hub.settings.getTheme("selected/fill")
        color_selected.setAlpha(hub.settings.get("display/alpha"))
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

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        xw.writeStartElement("fill")
        xw.writeAttribute("color", val2str(self.color))
        xw.writeAttribute("style", val2str(self.style))
        xw.writeEndElement()

    @classmethod
    def fromXml(cls : Self, xr : QXmlStreamReader) -> Self:
        attributes = xr.attributes()
        xr.readNext()
        inst : Fill = cls()
        for attr in attributes:
            match attr.name():
                case "color":
                    inst.setColor(str2val(attr.value(), QColor))
                case "style":
                    inst.setStyle(str2val(attr.value(), Qt.BrushStyle))
        return inst


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
