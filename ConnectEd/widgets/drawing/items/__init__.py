import uuid

from typing      import Optional, Self, Optional, Callable, Any
from types       import SimpleNamespace
from dataclasses import dataclass
from enum        import Enum

from PyQt6.QtCore    import Qt, QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtGui     import QPen, QBrush, QColor, QFont, QAction, QUndoCommand
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsSceneContextMenuEvent, QMenu

from ....core import Z_DRAWING, logger, \
                     val2str, str2val, camel_to_proper, toXmlAttrs, fromXmlAttrs

from .... import hub

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..             import DrawingView, DrawingScene
    from .property_text import PropertyText


class Default:
    def __str__(self): return "default"
    def __repr__(self): return "<default>"

DEFAULT = Default()

class NoChange:
    def __str__(self): return "no change"
    def __repr__(self): return "<no change>"

NO_CHANGE = NoChange()


class Edge(Enum):
    LEFT   = "left"
    RIGHT  = "right"
    TOP    = "top"
    BOTTOM = "bottom"

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
class AttrSpec:
    name      : str
    type_name : str
    exists    : Callable[[Any], bool]
    getter    : Callable[[Any], Any]
    setter    : Callable[[Any, Any], None]

    @property
    def tag(self) -> str:
        return self.name.lower().replace(" ", "_")

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

class LinePen:
    element  : "ElementMixin"
    color    : Default | QColor
    width    : Default | float
    style    : Default | Qt.PenStyle
    normal   : QPen
    selected : QPen
    pen      : QPen

    def __init__(
        self    : Self,
        element : "ElementMixin",
        pref    : LinePref = LinePref(DEFAULT, DEFAULT, DEFAULT)
    ) -> None:
        self.element  = element
        self.color    = pref.color
        self.width    = pref.width
        self.style    = pref.style
        self.normal   = QPen()
        self.normal.setCapStyle(element._CAP_STYLE)
        self.normal.setJoinStyle(element._JOIN_STYLE)
        self.selected = QPen()
        self.selected.setCapStyle(element._CAP_STYLE)
        self.selected.setJoinStyle(element._JOIN_STYLE)
        self.onSettingsChange()

    def getColor(self : Self) -> QColor:
        return self.color

    def setColor(self : Self, color : QColor) -> None:
        self.color = color
        self.onSettingsChange()

    def getWidth(self : Self) -> float:
        return self.width

    def setWidth(self : Self, width : float) -> None:
        self.width = width
        self.onSettingsChange()

    def getStyle(self : Self) -> Qt.PenStyle:
        return self.style

    def setStyle(self : Self, style : Qt.PenStyle) -> None:
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
        settings_name = self.element.__class__.__name__
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
        self.onSelectionChange(self.element.isSelected())

    def onSelectionChange(self : Self, selected : bool) -> None:
        self.pen = self.selected if selected else self.normal

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
        inst : LinePen = cls()
        for attr in attributes:
            match attr.name():
                case "color":
                    inst.setColor(str2val(attr.value(), QColor))
                case "width":
                    inst.setWidth(str2val(attr.value(), float))
                case "style":
                    inst.setStyle(str2val(attr.value(), Qt.PenStyle))
        return inst

class FillBrush:
    element  : "ElementMixin"
    color    : Default | QColor
    style    : Default | Qt.BrushStyle
    normal   : QBrush
    selected : QBrush
    brush    : QBrush

    def __init__(
        self    : Self,
        element : "ElementMixin",
        pref    : FillPref = FillPref(DEFAULT, DEFAULT)
    ) -> None:
        self.element  = element
        self.color    = pref.color
        self.style    = pref.style
        self.normal   = QBrush()
        self.selected = QBrush()
        self.onSettingsChange()

    def getColor(self : Self) -> QColor:
        return self.color

    def setColor(self : Self, color : QColor) -> None:
        self.color = color
        self.onSettingsChange()

    def getStyle(self : Self) -> Qt.BrushStyle:
        return self.style

    def setStyle(self : Self, style : Qt.BrushStyle) -> None:
        self.style = style
        self.onSettingsChange()

    def getPref(self : Self) -> FillPref:
        return FillPref(self.color, self.style)

    def setPref(self : Self, c : FillPref | FillPrefChange) -> None:
        if c.color is not NO_CHANGE: self.color = c.color
        if c.style is not NO_CHANGE: self.style = c.style
        self.onSettingsChange()

    def getDefaults(self : Self) -> SimpleNamespace:
        settings_name = self.element.__class__.__name__
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
        self.onSelectionChange(self.element.isSelected())

    def onSelectionChange(self : Self, selected : bool) -> None:
        self.brush = self.selected if selected else self.normal

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        xw.writeStartElement("fill")
        xw.writeAttribute("color", val2str(self.color))
        xw.writeAttribute("style", val2str(self.style))
        xw.writeEndElement()

    @classmethod
    def fromXml(cls : Self, xr : QXmlStreamReader) -> Self:
        attributes = xr.attributes()
        xr.readNext()
        inst : FillBrush = cls()
        for attr in attributes:
            match attr.name():
                case "color":
                    inst.setColor(str2val(attr.value(), QColor))
                case "style":
                    inst.setStyle(str2val(attr.value(), Qt.BrushStyle))
        return inst

class QuillColorFont:
    element   : "ElementMixin"
    color     : Default | QColor
    family    : Default | str
    size      : Default | float
    bold      : Default | bool
    italic    : Default | bool
    underline : Default | bool
    normal    : QColor
    selected  : QColor
    current   : QColor
    font      : QFont

    def __init__(
        self    : Self,
        element : "ElementMixin",
        pref    : QuillPref = \
                  QuillPref(DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT)
    ) -> None:
        self.element   = element
        self.color     = pref.color
        self.family    = pref.family
        self.size      = pref.size
        self.bold      = pref.bold
        self.italic    = pref.italic
        self.underline = pref.underline
        self.normal    = QColor()
        self.selected  = QColor()
        self.font      = QFont()
        self.onSettingsChange()

    def getColor(self : Self) -> QColor:
        return self.color

    def setColor(self : Self, color : QColor) -> None:
        self.color = color
        self.onSettingsChange()

    def getFamily(self : Self) -> str:
        return self.family

    def setFamily(self : Self, family : str) -> None:
        self.family = family
        self.onSettingsChange()

    def getSize(self : Self) -> float:
        return self.size

    def setSize(self : Self, size : float) -> None:
        self.size = size
        self.onSettingsChange()

    def getBold(self : Self) -> bool:
        return self.bold

    def setBold(self : Self, bold : bool) -> None:
        self.bold = bold
        self.onSettingsChange()

    def getItalic(self : Self) -> bool:
        return self.italic

    def setItalic(self : Self, italic : bool) -> None:
        self.italic = italic
        self.onSettingsChange()

    def getUnderline(self : Self) -> bool:
        return self.underline

    def setUnderline(self : Self, underline : bool) -> None:
        self.underline = underline
        self.onSettingsChange()

    def getPref(self : Self) -> QuillPref:
        return QuillPref(
            self.color,
            self.family,
            self.size,
            self.bold,
            self.italic,
            self.underline
        )

    def setPref(self : Self, c : QuillPref | QuillPrefChange) -> None:
        if c.color     is not NO_CHANGE: self.color     = c.color
        if c.family    is not NO_CHANGE: self.family    = c.family
        if c.size      is not NO_CHANGE: self.size      = c.size
        if c.bold      is not NO_CHANGE: self.bold      = c.bold
        if c.italic    is not NO_CHANGE: self.italic    = c.italic
        if c.underline is not NO_CHANGE: self.underline = c.underline
        self.onSettingsChange()

    def getDefaults(self : Self) -> SimpleNamespace:
        settings_name = self.element.__class__.__name__
        return hub.settings.getTheme(f"elements/{settings_name}/text")

    def onSettingsChange(self : Self) -> None:
        default = self.getDefaults()
        self.selected.setRgb(hub.settings.getTheme("selected/text").rgb())
        self.selected.setAlpha(hub.settings.get("display/alpha"))
        self.normal.setRgb(
            default.color.rgb() if self.color is DEFAULT else self.color.rgb()
        )
        self.normal.setAlpha(hub.settings.get("display/alpha"))
        self.font.setFamily(
            default.family if self.family is DEFAULT else self.family
        )
        self.font.setPointSizeF(
            default.size if self.size is DEFAULT else self.size
        )
        self.font.setBold(
            default.bold if self.bold is DEFAULT else self.bold
        )
        self.font.setItalic(
            default.italic if self.italic is DEFAULT else self.italic
        )
        self.font.setUnderline(
            default.underline if self.underline is DEFAULT else self.underline
        )
        if hasattr(self.element, "setDefaultFont"):
            self.element.setDefaultFont(self.font)
        elif hasattr(self.element, "setFont"):
            self.element.setFont(self.font)
        self.onSelectionChange(self.element.isSelected())

    def onSelectionChange(self : Self, selected : bool) -> None:
        self.current = self.selected if selected else self.normal
        if hasattr(self.element, "setDefaultTextColor"):
            self.element.setDefaultTextColor(self.current)
        elif hasattr(self.element, "setColor"):
            self.element.setColor(self.current)

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        xw.writeStartElement("text")
        xw.writeAttribute( "color",     val2str( self.color     ))
        xw.writeAttribute( "family",    val2str( self.family    ))
        xw.writeAttribute( "size",      val2str( self.size      ))
        xw.writeAttribute( "bold",      val2str( self.bold      ))
        xw.writeAttribute( "italic",    val2str( self.italic    ))
        xw.writeAttribute( "underline", val2str( self.underline ))
        xw.writeEndElement()

    @classmethod
    def fromXml(cls : Self, xr : QXmlStreamReader) -> Self:
        attributes = xr.attributes()
        xr.readNext()
        element_text : QuillColorFont = cls()
        for attr in attributes:
            v = attr.value()
            match attr.name():
                case "color"     : element_text.setColor(str2val(v, QColor))
                case "family"    : element_text.setFamily(str2val(v, str))
                case "size"      : element_text.setSize(str2val(v, float))
                case "bold"      : element_text.setBold(str2val(v, bool))
                case "italic"    : element_text.setItalic(str2val(v, bool))
                case "underline" : element_text.setUnderline(str2val(v, bool))
        return element_text

class OutlinePen:
    pen : QPen

    def __init__(self : Self) -> None:
        self.pen = QPen()
        self.onSettingsChange()

    def onSettingsChange(self : Self) -> None:
        self.pen.setColor(hub.settings.getTheme("selected/line"))
        self.pen.setWidthF(hub.settings.get("display/select/outline/width"))
        self.pen.setStyle(hub.settings.get("display/select/outline/style"))

class ElementKeypointsMixin:
    _KEY_POINTS : Optional[list["KP"]] = None
    _ANCHORED   : bool = False

    _kpm : "KPManager"

    def initKeypoints(self : Self) -> None:
        self._kpm = KPManager(self, self._KEY_POINTS)

    def hasAnchor(self : Self) -> bool:
        return hasattr(self, "_kpm") and self._kpm.anchor is not None

    def anchor(self : Self) -> "KP":
        if hasattr(self, "_kpm"):
            return self._kpm.anchor_loc
        else:
            raise NotImplementedError("anchor() is not implemented")

    def setAnchor(self : Self, anchor : "KP") -> None:
        if hasattr(self, "_kpm"):
            self._kpm.setAnchor(anchor)
        else:
            raise NotImplementedError("setAnchor() is not implemented")

class ElementLineMixin:
    _CAP_STYLE  = Qt.PenCapStyle.SquareCap
    _JOIN_STYLE = Qt.PenJoinStyle.MiterJoin
    _ATTR_SPECS_LINE = [
        AttrSpec(
            name      = "Line Color",
            type_name = "QColor",
            exists    = lambda self: self.line is not None,
            getter    = lambda self: self.line.getColor(),
            setter    = lambda self, value: self.line.setColor(value)
        ),
        AttrSpec(
            name      = "Line Width",
            type_name = "float",
            exists    = lambda self: self.line is not None,
            getter    = lambda self: self.line.getWidth(),
            setter    = lambda self, value: self.line.setWidth(value)
        ),
        AttrSpec(
            name      = "Line Style",
            type_name = "Qt.PenStyle",
            exists    = lambda self: self.line is not None,
            getter    = lambda self: self.line.getStyle(),
            setter    = lambda self, value: self.line.setStyle(value)
        )
    ]

    line : LinePen

    def initLine(self : Self):
        self.line = LinePen(self)

class ElementFillMixin:
    _ATTR_SPECS_FILL = [
        AttrSpec(
            name      = "Fill Color",
            type_name = "QColor",
            exists    = lambda self: self.fill is not None,
            getter    = lambda self: self.fill.getColor(),
            setter    = lambda self, value: self.fill.setColor(value)
        ),
        AttrSpec(
            name      = "Fill Style",
            type_name = "Qt.BrushStyle",
            exists    = lambda self: self.fill is not None,
            getter    = lambda self: self.fill.getStyle(),
            setter    = lambda self, value: self.fill.setStyle(value)
        )
    ]

    fill : FillBrush

    def initFill(self : Self):
        self.fill = FillBrush(self)

class ElementQuillMixin:
    _ATTR_SPECS_QUILL = [
        AttrSpec(
            name      = "Text Color",
            type_name = "QColor",
            exists    = lambda self: self.quill is not None,
            getter    = lambda self: self.quill.getColor(),
            setter    = lambda self, value: self.quill.setColor(value)
        ),
        AttrSpec(
            name      = "Text Font",
            type_name = "str",
            exists    = lambda self: self.quill is not None,
            getter    = lambda self: self.quill.getFamily(),
            setter    = lambda self, value: self.quill.setFamily(value)
        ),
        AttrSpec(
            name      = "Text Size",
            type_name = "float",
            exists    = lambda self: self.quill is not None,
            getter    = lambda self: self.quill.getSize(),
            setter    = lambda self, value: self.quill.setSize(value)
        ),
        AttrSpec(
            name      = "Text Bold",
            type_name = "bool",
            exists    = lambda self: self.quill is not None,
            getter    = lambda self: self.quill.getBold(),
            setter    = lambda self, value: self.quill.setBold(value)
        ),
        AttrSpec(
            name      = "Text Italic",
            type_name = "bool",
            exists    = lambda self: self.quill is not None,
            getter    = lambda self: self.quill.getItalic(),
            setter    = lambda self, value: self.quill.setItalic(value)
        ),
        AttrSpec(
            name      = "Text Underline",
            type_name = "bool",
            exists    = lambda self: self.quill is not None,
            getter    = lambda self: self.quill.getUnderline(),
            setter    = lambda self, value: self.quill.setUnderline(value)
        )
    ]

    quill : QuillColorFont

    def initQuill(self : Self):
        self.quill = QuillColorFont(self)

class ElementOutlineMixin:
    outline : OutlinePen

    def initOutline(self : Self):
        self.outline = OutlinePen()

class ElementChangeMixin:
    def itemChange(
        self   : QGraphicsItem,
        change : QGraphicsItem.GraphicsItemChange,
        value  : Any
    ) -> Any:
        match change:
            case QGraphicsItem.GraphicsItemChange.ItemParentHasChanged:
                if hasattr(self, 'onParentChange'):
                    self.onParentChange(value)
            case QGraphicsItem.GraphicsItemChange.ItemSceneHasChanged:
                if hasattr(self, 'onSceneChange'):
                    self.onSceneChange(value)
            case QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
                if hasattr(self, 'onPositionChange'):
                    self.onPositionChange(value)
            case QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
                if hasattr(self, 'onSelectionChange'):
                    self.onSelectionChange(value)
        return super().itemChange(change, value)

    def onSettingsChange(self : Self) -> None:
        self.prepareGeometryChange()
        if hasattr(self, "line"): self.line.onSettingsChange()
        if hasattr(self, "fill"): self.fill.onSettingsChange()
        if hasattr(self, "quill"): self.quill.onSettingsChange()
        if hasattr(self, "outline"): self.outline.onSettingsChange()
        self.onGeometryChange()

    def onGeometryChange(self : Self) -> None:
        raise NotImplementedError(
            f"onGeometryChange() is not implemented in {self.__class__.__name__}"
        )

    def onSelectionChange(self : Self, selected : bool) -> None:
        if hasattr(self, "line"): self.line.onSelectionChange(selected)
        if hasattr(self, "fill"): self.fill.onSelectionChange(selected)
        if hasattr(self, "quill"): self.quill.onSelectionChange(selected)
        if self._kpm is not None:
            self._kpm.onSelectionChange(selected)
        self.update()

class ElementMenuMixin:
    def contextMenuEvent(
        self  : Self,
        event : QGraphicsSceneContextMenuEvent
    ) -> None:
        items = self.getMenuItems()  # subclass must provide this method
        if len(items) == 0:
            return
        pos = event.screenPos()
        menu = QMenu()
        for item in items:
            if item.startswith("-"):
                menu.addSeparator()
            else:
                from .. import getView
                view = getView(pos)
                slot_name = f"ctxMenu{item.replace(' ', '').replace('.', '')}"
                if hasattr(self, slot_name):
                    slot = getattr(self, slot_name)
                    action = QAction(item, menu)
                    action.triggered.connect(
                        lambda checked=False, w=view, s=slot: s(checked, w)
                    )
                    menu.addAction(action)
                else:
                    logger.error(f"{slot_name} missing from {self.__class__.__name__}")
        menu.exec(pos)

    def ctxMenuAppearance(
        self    : Self,
        checked : bool,
        view    : "DrawingView"
    ) -> None:
        view.editAppearance(self)

    def ctxMenuProperties(
        self    : Self,
        checked : bool,
        view    : "DrawingView"
    ) -> None:
        view.editProperties(self)

class PropertiesMixin:
    """Mixin for elements and scenes that have properties."""
    _ATTR_SPECS         : list[AttrSpec]         = []
    _ATTR_SPECS_BY_NAME : dict[str, AttrSpec]    = {}
    _ATTR_SPECS_BY_TAG  : dict[str, AttrSpec]    = {}
    _PROPERTIES         : dict[str, str | tuple] = {}

    properties : dict[str, str]

    def initProperties(self : Self, bare : bool = False) -> None:
        self._ATTR_SPECS_BY_NAME = {spec.name: spec for spec in self._ATTR_SPECS}
        self._ATTR_SPECS_BY_TAG = {spec.tag: spec for spec in self._ATTR_SPECS}
        self.properties = {}
        if not bare and self._PROPERTIES is not None:
            for name, value in self._PROPERTIES.items():
                if name in self._ATTR_SPECS_BY_NAME:
                    logger.error(f"Custom/inherent property clash: {name}")
                    return
                if name in self.properties:
                    logger.error(f"Duplicate property: {name}")
                    return
                if isinstance(value, tuple):
                    value, display, anchor, pos, cleat = value
                    self.properties[name] = value
                    p = PropertyText(name, display, pos, anchor, cleat)
                    p.setParentItem(self)
                elif isinstance(value, str):
                    self.properties[name] = value
                else:
                    logger.error(f"Invalid property value: {value}")
                    return

    def getAttributes(self : Self) -> list[str]:
        return self._ATTR_SPECS_BY_NAME.keys()

    def hasAttribute(self : Self, name: str) -> bool:
        return False if name not in self._ATTR_SPECS_BY_NAME else \
            self._ATTR_SPECS_BY_NAME[name].exists(self)

    def getAttributeTypeName(self : Self, name: str) -> str | None:
        if name not in self._ATTR_SPECS_BY_NAME:
            logger.warning(f"Attribute not found: {name}")
            return None
        return self._ATTR_SPECS_BY_NAME[name].type_name

    def getAttribute(self : Self, name: str) -> str| None:
        if name not in self._ATTR_SPECS_BY_NAME:
            logger.warning(f"Attribute not found: {name}")
            return None
        return self._ATTR_SPECS_BY_NAME[name].getter(self)

    def setAttribute(self : Self, name: str, value: Any) -> None:
        if name not in self._ATTR_SPECS_BY_NAME:
            logger.warning(f"Attribute not found: {name}")
            return
        self._ATTR_SPECS_BY_NAME[name].setter(self, value)

    def getProperties(self : Self) -> list[str]:
        return sorted(self.properties.keys())

    def hasProperty(self : Self, name: str) -> bool:
        return False if self.properties is None else name in self.properties

    def getProperty(self: Self, name: str) -> str| None:
        """Get a property value, returning empty string if not found."""
        if name not in self.properties:
            logger.warning(f"Property not found: {name}")
            return None
        return self.properties[name]

    def setProperty(self: Self, name: str, value: str) -> None:
        """Set a property value update affected PropertyText instance(s)."""
        self.properties[name] = value
        for item in self.childItems():
            if isinstance(item, PropertyText) and item.name() == name:
                item.setProperty(name, value)

    def deleteProperty(self: Self, name: str) -> None:
        """Delete a property and emit signal to notify PropertyText objects."""
        if name not in self.properties:
            logger.warning(f"Property not found: {name}")
            return
        del self.properties[name]
        for item in self.childItems():
            if isinstance(item, PropertyText) and item.name() == name:
                item.setParentItem(None)
                scene = self.scene()
                scene.removeItem(item)
                del item

    def getPropAttr(self : Self, name: str) -> str| None:
        if name in self.properties:
            return self.properties[name]
        elif name in self._ATTR_SPECS_BY_NAME:
            attr_spec = self._ATTR_SPECS_BY_NAME[name]
            if attr_spec.exists(self):
                return val2str(attr_spec.getter(self))
            else:
                return None
        else:
            logger.warning(f"Property or attribute not found: {name}")
            return None

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        for name, value in self.properties.items():
            xw.writeStartElement("property")
            xw.writeAttribute("name", name)
            xw.writeAttribute("value", value)
            xw.writeEndElement()

    def fromXml(self : Self, xr : QXmlStreamReader) -> None:
        while not xr.isStartElement() and not xr.isEndElement():
            xr.readNext()
        while xr.isStartElement() and xr.name() == "property":
            name = xr.attributes().value("name")
            if name is not None:
                value = xr.attributes().value("value")
                self.setProperty(name, value)
            xr.readNext()
            if xr.isEndElement():
                xr.readNext()
            while not xr.isStartElement() and not xr.isEndElement():
                xr.readNext()

class ElementCloneMixin:
    def clone(self : Self, original : Optional[Self] = None) -> Self:
        """Create a clone of this element with a new UUID."""
        source = original if original is not None else self
        clone = self.__class__(bare=True)
        # clone attributes
        if hasattr(source, "_ATTR_SPECS"):
            for attr_spec in source._ATTR_SPECS:
                if attr_spec.exists(source):
                    value = attr_spec.getter(source)
                    attr_spec.setter(clone, value)
        # clone properties, property texts, and pins
        if hasattr(source, "properties"):
            clone.properties = source.properties.copy()
        from .port_pin import BasePin
        for item in source.childItems():
            if isinstance(item, BasePin):
                clone_pin = item.clone(item)
                clone_pin.setParentItem(clone)
            elif isinstance(item, PropertyText):
                item.clone().setParentItem(clone)
        clone.onGeometryChange()
        return clone

class ElementXmlMixin:
    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        xw.writeStartElement(self.__class__.__name__)
        toXmlAttrs(self, xw)
        PropertiesMixin.toXml(self, xw)
        from .port_pin import BasePin
        for item in self.childItems():
            if isinstance(item, PropertyText):
                item.toXml(xw)
            elif isinstance(item, BasePin):
                item.toXml(xw)
        xw.writeEndElement()

    @classmethod
    def fromXml(cls : Self, xr: QXmlStreamReader) -> Self:
        instance = cls(bare=True)
        fromXmlAttrs(instance, xr)
        # check if we're already at the end element (self-closing)
        if xr.isEndElement() and xr.name() == cls.__name__:
            return instance
        # read properties
        PropertiesMixin.fromXml(instance, xr)
        # read child PropertyText and BasePin elements
        while not (xr.isEndElement() and xr.name() == cls.__name__):
            if xr.isStartElement():
                if xr.name() == "PropertyText":
                    from .property_text import PropertyText
                    p : PropertyText = PropertyText.fromXml(xr)
                    p.setParentItem(instance)
                elif xr.name() == "BlockPin":
                    from .port_pin import BlockPin
                    pin : BlockPin = BlockPin.fromXml(xr)
                    pin.setParentItem(instance)
                else:
                    logger.warning(f"Unexpected child element: {xr.name()}")
            xr.readNext()
        return instance

class ElementMixin(ElementChangeMixin, ElementCloneMixin, ElementXmlMixin, PropertiesMixin):
    """Mixin class for all elements."""
    Z = Z_DRAWING
    _CAP_STYLE = Qt.PenCapStyle.SquareCap
    _JOIN_STYLE = Qt.PenJoinStyle.MiterJoin
    _ATTR_SPECS_BASIC = [
        AttrSpec(
            name      = "Anchor",
            type_name = "KP",
            exists    = lambda self: self.hasAnchor(),
            getter    = lambda self: self.anchor(),
            setter    = lambda self, value: self.setAnchor(value)
        ),
        AttrSpec(
            name      = "Position X",
            type_name = "float",
            exists    = lambda self: True,
            getter    = lambda self: self.pos().x(),
            setter    = lambda self, value: self.setPosX(value)
        ),
        AttrSpec(
            name      = "Position Y",
            type_name = "float",
            exists    = lambda self: True,
            getter    = lambda self: self.pos().y(),
            setter    = lambda self, value: self.setPosY(value)
        )
    ]

    uuid           : str

    def initElement(self : Self, bare : bool = False) -> None:
        self.resetUuid()
        if hasattr(self, "initLine"):
            self.initLine()
        if hasattr(self, "initFill"):
            self.initFill()
        if hasattr(self, "initQuill"):
            self.initQuill()
        if hasattr(self, "initOutline"):
            self.initOutline()
        self.setZValue(self.Z)
        f = QGraphicsItem.GraphicsItemFlag
        self.setFlag( f.ItemIsSelectable              , True )
        self.setFlag( f.ItemSendsGeometryChanges      , True )
        self.setFlag( f.ItemSendsScenePositionChanges , True )
        self.setCacheMode(QGraphicsItem.CacheMode.DeviceCoordinateCache)
        hub.settings.changed.connect(self.onSettingsChange)
        if hasattr(self, "initKeypoints"):
            self.initKeypoints()
        self.initProperties(bare)

    def __hash__(self):
        return hash(self.uuid)

    def __eq__(self, other):
        if not isinstance(other, ElementMixin):
            return NotImplemented
        return self.uuid == other.uuid

    def setPosX(self : Self, value : float) -> None:
        pos = self.pos()
        pos.setX(value)
        self.setPos(pos)

    def setPosY(self : Self, value : float) -> None:
        pos = self.pos()
        pos.setY(value)
        self.setPos(pos)

    def resetUuid(self : Self) -> None:
        self.uuid = str(uuid.uuid4())

class cmdElement(QUndoCommand):
    """Base class for all commands that work with an element."""
    _scene   : "DrawingScene"
    _element : ElementMixin

    def __init__(
        self    : Self,
        scene   : "DrawingScene",
        element : ElementMixin
    ):
        text = camel_to_proper(self.__class__.__name__.replace("cmd", ""))
        super().__init__(text)
        self._scene = scene
        self._element = element

    def id(self : Self) -> int:
        """Return a unique ID for merging commands."""
        element_id = id(self._element) & 0x7FFFFFFF
        class_id = hash(self.__class__.__name__) & 0x7FFFFFFF
        return ((element_id + class_id) & 0x7FFFFFFF)

    def mergeWith(self : Self, other : QUndoCommand) -> bool:
        """Merge this command with another identical command."""
        if not isinstance(other, self.__class__) \
        or other._scene != self._scene \
        or other._element != self._element:
            return False
        return True

    def redo(self : Self) -> None:
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement redo"
        )

    def undo(self : Self) -> None:
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement undo"
        )

class cmdElements(QUndoCommand):
    """Base class for all commands that work with multiple elements."""
    _scene    : "DrawingScene"
    _elements : list[ElementMixin]

    def __init__(
        self     : Self,
        scene    : "DrawingScene",
        elements : list[ElementMixin]
    ):
        text = camel_to_proper(self.__class__.__name__.replace("cmd", ""))
        QUndoCommand.__init__(self, text)
        self._scene = scene
        self._elements = elements

    def id(self : Self) -> int:
        """Return a unique ID for merging commands."""
        element_ids = [id(element) & 0x7FFFFFFF for element in self._elements]
        class_id = hash(self.__class__.__name__) & 0x7FFFFFFF
        return ((sum(element_ids) + class_id) & 0x7FFFFFFF)

    def mergeWith(self : Self, other : QUndoCommand) -> bool:
        """Merge this command with another identical command."""
        if not isinstance(other, self.__class__) \
        or other._scene != self._scene \
        or other._elements != self._elements:
            return False
        return True

    def redo(self : Self) -> None:
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement redo"
        )

    def undo(self : Self) -> None:
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement undo"
        )

class cmdPlaceElement(cmdElement):
    """Base class for all commands that place an element."""

    def __init__(
        self    : Self,
        scene   : "DrawingScene",
        element : ElementMixin
    ):
        super().__init__(scene, element) # record scene and element instances

    def redo(self : Self) -> None:
        if self._element.scene() != self._scene:
            self._scene.addItem(self._element)

    def undo(self : Self) -> None:
        self._scene.removeItem(self._element)

def clone(elements : list[ElementMixin]) -> list[ElementMixin]:
    r = []
    for element in elements:
        try:
            r.append(element.clone())
        except Exception as e:
            logger.warning(f"Failed to clone element {element}: {e}")
    return r

__all__ = [
    "Default",
    "DEFAULT",
    "NoChange",
    "NO_CHANGE",
    "Edge",
    "EdgeLoc",
    "SignalDirection",
    "RangeDirection",
    "VectorRange",
    "AttrSpec",
    "LineSpec",
    "LinePref",
    "LinePrefChange",
    "FillSpec",
    "FillPref",
    "FillPrefChange",
    "QuillSpec",
    "QuillPref",
    "QuillPrefChange",
    "ElementMixin",
    "cmdElement",
    "cmdElements",
    "cmdPlaceElement",
    "clone"
]
from .key_point import KP, KPReverse, KeyPoint, KPDef, KPManager
__all__ += key_point.__all__
from .tether_text import TetherText, Tether
__all__ += tether_text.__all__
from .property_text import PropertyDisplay, PropertyText
__all__ += property_text.__all__
from .text import Text, cmdPlaceText
__all__ += text.__all__
from .text_block import TextBlock, cmdPlaceTextBlock
__all__ += text_block.__all__
from .rectangle import Rectangle, cmdPlaceRectangle
__all__ += rectangle.__all__
from .port_pin import Port, cmdPlacePort, BlockPin
__all__ += port_pin.__all__
from .block import Block, cmdPlaceBlock
__all__ += block.__all__
from .symbol_instance import SymbolInstance
__all__ += symbol_instance.__all__

element_class_dict = {}
for class_name in __all__:
    element_class_dict[class_name] = globals()[class_name]
__all__ += ["element_class_dict"]
