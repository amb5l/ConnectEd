from typing      import Optional, Self
from types       import SimpleNamespace
from dataclasses import dataclass
from enum        import Enum

from PyQt6.QtCore    import Qt, QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtGui     import QPen, QBrush, QColor, QFont

from .... import hub

from ....core.log   import logger
from ....core.utils import val2str, str2val

from .mixin import ElementMixin


class Default:
    def __str__(self): return "default"
    def __repr__(self): return "<default>"

DEFAULT = Default()

class NoChange:
    def __str__(self): return "no change"
    def __repr__(self): return "<no change>"

NO_CHANGE = NoChange()

class APType(Enum):
    Static  = 0
    Mover   = 1
    Resizer = 2

class Edge(Enum):
    LEFT   = "Left"
    RIGHT  = "Right"
    TOP    = "Top"
    BOTTOM = "Bottom"

@dataclass
class EdgeLoc:
    edge     : Optional[Edge]  = None
    distance : Optional[float] = None

    def toStr(self) -> str:
        return f"{self.edge.value},{self.distance}" \
              if self.edge is not None else "None"

    @classmethod
    def fromStr(cls, s : str) -> Self:
        edge, distance = s.split(",")
        return cls(Edge(edge), float(distance))

# TODO: consider passive, 3-state etc for EE schematics
class SignalDirection(Enum):
    IN  = "in"
    OUT = "out"
    BI  = "bi"

class RangeDirection(Enum):
    UNSPECIFIED = ":"
    DOWN        = "\u25bc"
    UP          = "\u25b2"

class VectorRange:
    left  : str            # left value (may refer to parameter/generic)
    dir   : RangeDirection # down or up
    right : str            # right value (may refer to parameter/generic)

    def __init__(self, left : str, dir : RangeDirection, right : str) -> None:
        self.left  = left
        self.dir   = dir
        self.right = right

@dataclass
class LineSpec:
    color : QColor
    width : float
    style : Qt.PenStyle

@dataclass
class LinePref:
    color : Default | QColor      = DEFAULT
    width : Default | float       = DEFAULT
    style : Default | Qt.PenStyle = DEFAULT

    def toStr(self):
        s_c = "default" if self.color is DEFAULT else \
            hex(self.color.rgba())
        s_w = "default" if self.width is DEFAULT else \
            str(self.width)
        s_s = "default" if self.style is DEFAULT else \
            str(self.style).replace("PenStyle.", "")
        return f"{s_c},{s_w},{s_s}"

    @classmethod
    def fromStr(cls, s : str) -> Self:
        s_c, s_w, s_s = s.split(",")
        color = DEFAULT if s_c == "default" else QColor(int(s_c, 16))
        width = DEFAULT if s_w == "default" else float(s_w)
        style = DEFAULT if s_s == "default" else Qt.PenStyle[s_s]
        return cls(color, width, style)

@dataclass
class LinePrefDefault:
    color : Optional[ Default | QColor      ] = None
    width : Optional[ Default | float       ] = None
    style : Optional[ Default | Qt.PenStyle ] = None

@dataclass
class LinePrefChange:
    color : Optional[ NoChange | Default | QColor      ] = None
    width : Optional[ NoChange | Default | float       ] = None
    style : Optional[ NoChange | Default | Qt.PenStyle ] = None

@dataclass
class FillSpec:
    color : QColor
    style : Qt.BrushStyle

@dataclass
class FillPref:
    color : Default | QColor        = DEFAULT
    style : Default | Qt.BrushStyle = DEFAULT

    def toStr(self):
        s_c = "default" if self.color is DEFAULT else \
            hex(self.color.rgba())
        s_s = "default" if self.style is DEFAULT else \
            str(self.style).replace("BrushStyle.", "")
        return f"{s_c},{s_s}"

    @classmethod
    def fromStr(cls, s : str) -> Self:
        s_c, s_s = s.split(",")
        color = DEFAULT if s_c == "default" else QColor(int(s_c, 16))
        style = DEFAULT if s_s == "default" else Qt.BrushStyle[s_s]
        return cls(color, style)

@dataclass
class FillPrefDefault:
    color : Optional[ Default | QColor        ] = None
    style : Optional[ Default | Qt.BrushStyle ] = None

@dataclass
class FillPrefChange:
    color : Optional[ NoChange | Default | QColor        ] = None
    style : Optional[ NoChange | Default | Qt.BrushStyle ] = None

@dataclass
class QuillSpec:
    color     : QColor
    family    : str
    size      : float
    bold      : bool
    italic    : bool
    underline : bool

@dataclass
class QuillPref:
    color     : Default | QColor = DEFAULT
    family    : Default | str    = DEFAULT
    size      : Default | float  = DEFAULT
    bold      : Default | bool   = DEFAULT
    italic    : Default | bool   = DEFAULT
    underline : Default | bool   = DEFAULT

    def toStr(self):
        s_c = "default" if self.color is DEFAULT else \
            hex(self.color.rgba())
        s_f = "default" if self.family is DEFAULT else \
            self.family
        s_s = "default" if self.size is DEFAULT else \
            str(self.size)
        s_b = "default" if self.bold is DEFAULT else \
            str(self.bold)
        s_i = "default" if self.italic is DEFAULT else \
            str(self.italic)
        s_u = "default" if self.underline is DEFAULT else \
            str(self.underline)
        return f"{s_c},{s_f},{s_s},{s_b},{s_i},{s_u}"

    @classmethod
    def fromStr(cls, s : str) -> Self:
        s_c, s_f, s_s, s_b, s_i, s_u = s.split(",")
        color     = DEFAULT if s_c == "default" else QColor(int(s_c, 16))
        family    = DEFAULT if s_f == "default" else s_f
        size      = DEFAULT if s_s == "default" else float(s_s)
        bold      = DEFAULT if s_b == "default" else s_b.lower() == "true"
        italic    = DEFAULT if s_i == "default" else s_i.lower() == "true"
        underline = DEFAULT if s_u == "default" else s_u.lower() == "true"
        return cls(color, family, size, bold, italic, underline)

@dataclass
class QuillPrefDefault:
    color     : Optional[ Default | QColor ] = None
    family    : Optional[ Default | str    ] = None
    size      : Optional[ Default | float  ] = None
    bold      : Optional[ Default | bool   ] = None
    italic    : Optional[ Default | bool   ] = None
    underline : Optional[ Default | bool   ] = None

@dataclass
class QuillPrefChange:
    color     : Optional[ NoChange | Default | QColor ] = None
    family    : Optional[ NoChange | Default | str    ] = None
    size      : Optional[ NoChange | Default | float  ] = None
    bold      : Optional[ NoChange | Default | bool   ] = None
    italic    : Optional[ NoChange | Default | bool   ] = None
    underline : Optional[ NoChange | Default | bool   ] = None

@dataclass
class AppearanceSpec:
    line  : Optional[LineSpec]  = None
    fill  : Optional[FillSpec]  = None
    quill : Optional[QuillSpec] = None

@dataclass
class AppearancePref:
    line  : Optional[LinePref]  = None
    fill  : Optional[FillPref]  = None
    quill : Optional[QuillPref] = None

@dataclass
class AppearancePrefChange:
    line  : Optional[LinePrefChange]  = None
    fill  : Optional[FillPrefChange]  = None
    quill : Optional[QuillPrefChange] = None

class Line:
    parent   : "ElementMixin"
    color    : Default | QColor
    width    : Default | float
    style    : Default | Qt.PenStyle
    normal   : QPen
    selected : QPen
    pen      : QPen

    def __init__(
        self   : Self,
        parent : "ElementMixin",
        pref   : LinePref = LinePref(DEFAULT, DEFAULT, DEFAULT)
    ) -> None:
        self.parent = parent
        self.color  = pref.color
        self.width  = pref.width
        self.style  = pref.style
        self.normal = QPen()
        self.normal.setCapStyle(parent._CAP_STYLE)
        self.normal.setJoinStyle(parent._JOIN_STYLE)
        self.selected = QPen()
        self.selected.setCapStyle(parent._CAP_STYLE)
        self.selected.setJoinStyle(parent._JOIN_STYLE)
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
        return hub.settings.getTheme(f"elements/{settings_name}/line")

    def onSettingsChange(self : Self) -> None:
        default = self.getDefaults()
        color_normal = default.color if self.color is DEFAULT else self.color
        color_normal.setAlpha(hub.settings.get("display/alpha"))
        color_selected = hub.settings.getTheme("selected/line")
        color_selected.setAlpha(hub.settings.get("display/alpha"))
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

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        xw.writeStartElement("line")
        xw.writeAttribute("color", val2str(self.color))
        xw.writeAttribute("width", val2str(self.width))
        xw.writeAttribute("style", val2str(self.style))
        xw.writeEndElement()

    @classmethod
    def fromXml(cls : Self, xr : QXmlStreamReader) -> Self:
        attributes = xr.attributes()
        xr.readNext()
        inst : Line = cls()
        for attr in attributes:
            match attr.name():
                case "color":
                    inst.setColor(str2val(attr.value(), QColor))
                case "width":
                    inst.setWidth(str2val(attr.value(), float))
                case "style":
                    inst.setStyle(str2val(attr.value(), Qt.PenStyle))
        return inst

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

class Quill:
    _parent    : "ElementMixin"
    _color     : Default | QColor
    _family    : Default | str
    _size      : Default | float
    _bold      : Default | bool
    _italic    : Default | bool
    _underline : Default | bool
    _normal    : QColor
    _selected  : QColor
    _pen       : Optional[QPen]
    _brush     : Optional[QBrush]
    _font      : QFont

    def __init__(
        self   : Self,
        parent : "ElementMixin",
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
        settings_name = self._parent.__class__.__name__
        return hub.settings.getTheme(f"elements/{settings_name}/text")

    def onSettingsChange(self : Self) -> None:
        default = self.getDefaults()
        self._selected.setRgb(hub.settings.getTheme("selected/text").rgb())
        self._selected.setAlpha(hub.settings.get("display/alpha"))
        self._normal.setRgb(
            default.color.rgb() if self._color is DEFAULT else self._color.rgb()
        )
        self._normal.setAlpha(hub.settings.get("display/alpha"))
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

    def onSelectionChange(self : Self, selected : bool) -> None:
        color = self._selected if selected else self._normal
        if hasattr(self._parent, "setDefaultTextColor"):
            self._parent.setDefaultTextColor(color)
        else:
            self._brush.setColor(color)
            self._parent.setBrush(self._brush)

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        xw.writeStartElement("text")
        xw.writeAttribute( "color",     val2str( self._color     ))
        xw.writeAttribute( "family",    val2str( self._family    ))
        xw.writeAttribute( "size",      val2str( self._size      ))
        xw.writeAttribute( "bold",      val2str( self._bold      ))
        xw.writeAttribute( "italic",    val2str( self._italic    ))
        xw.writeAttribute( "underline", val2str( self._underline ))
        xw.writeEndElement()

    @classmethod
    def fromXml(cls : Self, xr : QXmlStreamReader) -> Self:
        attributes = xr.attributes()
        xr.readNext()
        inst : Quill = cls()
        for attr in attributes:
            v = attr.value()
            match attr.name():
                case "color"     : inst.setColor(str2val(v, QColor))
                case "family"    : inst.setFamily(str2val(v, str))
                case "size"      : inst.setSize(str2val(v, float))
                case "bold"      : inst.setBold(str2val(v, bool))
                case "italic"    : inst.setItalic(str2val(v, bool))
                case "underline" : inst.setUnderline(str2val(v, bool))
        return inst

class OutlinePen:
    pen : QPen

    def __init__(self : Self) -> None:
        self.pen = QPen()
        self.onSettingsChange()

    def onSettingsChange(self : Self) -> None:
        self.pen.setColor(hub.settings.getTheme("selected/line"))
        self.pen.setWidthF(hub.settings.get("display/select/outline/width"))
        self.pen.setStyle(hub.settings.get("display/select/outline/style"))

def clone(elements : list[ElementMixin]) -> list[ElementMixin]:
    r = []
    for element in elements:
        try:
            r.append(element.clone())
        except Exception as e:
            logger.warning(f"Failed to clone element {element}: {e}")
    return r

_element_classes = {}

def register_element(module_name: str, class_name: str):
    """Import a class from a submodule and register it in _element_classes."""
    import importlib
    module = importlib.import_module(f".{module_name}", package=__name__)
    cls = getattr(module, class_name)
    _element_classes[class_name] = cls
    return cls

register_element("port_pin", "Port")
register_element("block", "Block")
register_element("property_text", "PropertyText")
register_element("rectangle", "Rectangle")
register_element("text", "Text")
register_element("text_block", "TextBlock")
