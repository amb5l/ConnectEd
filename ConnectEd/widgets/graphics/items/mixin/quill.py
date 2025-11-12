from typing import Self
from types  import SimpleNamespace

from PyQt6.QtCore import Qt
from PyQt6.QtGui  import QColor, QFont, QPen, QBrush

from .....app import settings

from ...properties import PropertySpec

from .. import Default, DEFAULT, NO_CHANGE, Appearance, QuillPref, QuillPrefChange

from . import ItemMixin


class Quill:
    _parent    : "ItemMixin"
    _color     : Default | QColor
    _family    : Default | str
    _size      : Default | float
    _bold      : Default | bool
    _italic    : Default | bool
    _underline : Default | bool
    _normal    : QColor
    _selected  : QColor
    _pen       : QPen | None
    _brush     : QBrush | None
    _font      : QFont

    def __init__(
        self   : Self,
        parent : "ItemMixin",
        pref   : QuillPref = \
                  QuillPref(DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT)
    ) -> None:
        self._parent    = parent
        self._color     = pref.color
        self._family    = pref.family
        self._size      = pref.size
        self._bold      = pref.bold
        self._italic    = pref.italic
        self._underline = pref.underline
        self._normal = QColor()
        self._selected = QColor()
        self._font = QFont()
        if not hasattr(self._parent, "setDefaultTextColor"):
            self._pen = QPen()
            self._pen.setStyle(Qt.PenStyle.NoPen)
            self._brush = QBrush()
            self._brush.setStyle(Qt.BrushStyle.SolidPattern)
            self._parent.setPen(self._pen)
            self._parent.setBrush(self._brush)
        else:
            self._pen = None
            self._brush = None
        self._parent.setFont(self._font)
        self.onSettingsChange()

    def getColor(self : Self) -> Default | QColor:
        return self._color

    def setColor(self : Self, color : Default | QColor) -> None:
        self._color = color
        self.onSettingsChange()

    def getFamily(self : Self) -> Default | str:
        return self._family

    def setFamily(self : Self, family : Default | str) -> None:
        self._family = family
        self.onSettingsChange()

    def getSize(self : Self) -> Default | float:
        return self._size

    def setSize(self : Self, size : Default | float) -> None:
        self._size = size
        self.onSettingsChange()

    def getBold(self : Self) -> Default | bool:
        return self._bold

    def setBold(self : Self, bold : Default | bool) -> None:
        self._bold = bold
        self.onSettingsChange()

    def getItalic(self : Self) -> Default | bool:
        return self._italic

    def setItalic(self : Self, italic : Default | bool) -> None:
        self._italic = italic
        self.onSettingsChange()

    def getUnderline(self : Self) -> Default | bool:
        return self._underline

    def setUnderline(self : Self, underline : Default | bool) -> None:
        self._underline = underline
        self.onSettingsChange()

    def getPref(self : Self) -> QuillPref:
        return QuillPref(
            self._color,
            self._family,
            self._size,
            self._bold,
            self._italic,
            self._underline
        )

    def setPref(self : Self, c : QuillPref | QuillPrefChange) -> None:
        if c.color     is not NO_CHANGE: self._color     = c.color
        if c.family    is not NO_CHANGE: self._family    = c.family
        if c.size      is not NO_CHANGE: self._size      = c.size
        if c.bold      is not NO_CHANGE: self._bold      = c.bold
        if c.italic    is not NO_CHANGE: self._italic    = c.italic
        if c.underline is not NO_CHANGE: self._underline = c.underline
        self.onSettingsChange()

    def getDefaults(self : Self) -> SimpleNamespace:
        return settings().get(f"theme/items/{self._parent.settingsName()}/text")

    def onSettingsChange(self : Self) -> None:
        default = self.getDefaults()
        self._selected.setRgb(settings().get("theme/selected/text").rgb())
        self._selected.setAlpha(settings().get("display/alpha"))
        self._normal.setRgb(
            default.color.rgb() if self._color is DEFAULT else self._color.rgb()
        )
        self._normal.setAlpha(settings().get("display/alpha"))
        self._font.setFamily(
            default.family if self._family is DEFAULT else self._family
        )
        self._font.setPointSizeF(
            default.size if self._size is DEFAULT else self._size
        )
        self._font.setBold(
            default.bold if self._bold is DEFAULT else self._bold
        )
        self._font.setItalic(
            default.italic if self._italic is DEFAULT else self._italic
        )
        self._font.setUnderline(
            default.underline if self._underline is DEFAULT else self._underline
        )
        self._parent.setFont(self._font)
        self.onSelectionChange(self._parent.isSelected())
        if hasattr(self._parent, 'onGeometryChange'):
            self._parent.onGeometryChange()

    def onSelectionChange(self : Self, selected : bool) -> None:
        color = self._selected if selected else self._normal
        if hasattr(self._parent, "setDefaultTextColor"):
            self._parent.setDefaultTextColor(color)
        else:
            self._brush.setColor(color)
            self._parent.setBrush(self._brush)


class ItemQuillMixin:
    _PROPERTY_SPECS_QUILL = {
        "Text Color" : PropertySpec(
            type_name = "QColor",
            exists    = lambda self: self.a.quill is not None,
            getter    = lambda self: self.a.quill.getColor(),
            setter    = lambda self, value: self.a.quill.setColor(value),
            default   = lambda self: self.a.quill.getDefaults().color
        ),
        "Text Font" : PropertySpec(
            type_name = "FontFamily",  # a "subtype" of str - see str2val
            exists    = lambda self: self.a.quill is not None,
            getter    = lambda self: self.a.quill.getFamily(),
            setter    = lambda self, value: self.a.quill.setFamily(value),
            default   = lambda self: self.a.quill.getDefaults().family
        ),
        "Text Size" : PropertySpec(
            type_name = "FontSize",  # a "subtype" of float - see str2val
            exists    = lambda self: self.a.quill is not None,
            getter    = lambda self: self.a.quill.getSize(),
            setter    = lambda self, value: self.a.quill.setSize(value),
            default   = lambda self: self.a.quill.getDefaults().size
        ),
        "Text Bold" : PropertySpec(
            type_name = "bool",
            exists    = lambda self: self.a.quill is not None,
            getter    = lambda self: self.a.quill.getBold(),
            setter    = lambda self, value: self.a.quill.setBold(value),
            default   = lambda self: self.a.quill.getDefaults().bold
        ),
        "Text Italic" : PropertySpec(
            type_name = "bool",
            exists    = lambda self: self.a.quill is not None,
            getter    = lambda self: self.a.quill.getItalic(),
            setter    = lambda self, value: self.a.quill.setItalic(value),
            default   = lambda self: self.a.quill.getDefaults().italic
        ),
        "Text Underline" : PropertySpec(
            type_name = "bool",
            exists    = lambda self: self.a.quill is not None,
            getter    = lambda self: self.a.quill.getUnderline(),
            setter    = lambda self, value: self.a.quill.setUnderline(value),
            default   = lambda self: self.a.quill.getDefaults().underline
        )
    }

    a : Appearance

    def initQuill(self : Self):
        if not hasattr(self, "a"):
            self.a = Appearance()
        self.a.quill = Quill(self)
