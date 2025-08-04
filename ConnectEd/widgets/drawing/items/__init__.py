import uuid

from typing      import Optional, Self, Optional, Any
from types       import SimpleNamespace
from dataclasses import dataclass
from enum        import Enum

from PyQt6.QtCore    import Qt, QPointF, QRectF, \
                            QXmlStreamWriter, QXmlStreamReader
from PyQt6.QtGui     import QPen, QBrush, QColor, QFont, QPainterPath, \
                            QAction, QUndoCommand
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsSceneContextMenuEvent, QMenu

from ....core import Z_DRAWING, logger, \
                     val2str, str2val, camel_to_proper, toXmlAttrs, fromXmlAttrs

from ..properties import PropertySpec

from .... import hub

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingView, DrawingScene
    from .property_text import PropertyText


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

    def getColor(self : Self) -> QColor:
        return self._color

    def setColor(self : Self, color : QColor) -> None:
        self._color = color
        self.onSettingsChange()

    def getFamily(self : Self) -> str:
        return self._family

    def setFamily(self : Self, family : str) -> None:
        self._family = family
        self.onSettingsChange()

    def getSize(self : Self) -> float:
        return self._size

    def setSize(self : Self, size : float) -> None:
        self._size = size
        self.onSettingsChange()

    def getBold(self : Self) -> bool:
        return self._bold

    def setBold(self : Self, bold : bool) -> None:
        self._bold = bold
        self.onSettingsChange()

    def getItalic(self : Self) -> bool:
        return self._italic

    def setItalic(self : Self, italic : bool) -> None:
        self._italic = italic
        self.onSettingsChange()

    def getUnderline(self : Self) -> bool:
        return self._underline

    def setUnderline(self : Self, underline : bool) -> None:
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

class ElementMixin:
    Z = Z_DRAWING

    uuid : str

    def initElement(self : Self, bare : bool = False) -> None:
        f = QGraphicsItem.GraphicsItemFlag
        self.setFlag( f.ItemIsSelectable              , True )
        self.setFlag( f.ItemSendsGeometryChanges      , True )
        self.setFlag( f.ItemSendsScenePositionChanges , True )
        self.setCacheMode(QGraphicsItem.CacheMode.DeviceCoordinateCache)
        self.resetUuid()
        if hasattr(self, "initBoundShape"):
            self.initBoundShape()
        if hasattr(self, "initLine"):
            self.initLine()
        if hasattr(self, "initFill"):
            self.initFill()
        if hasattr(self, "initQuill"):
            self.initQuill()
        if hasattr(self, "initOutline"):
            self.initOutline()
        if hasattr(self, "initAnchorPoints"):
            self.initAnchorPoints()
        if hasattr(self, "initOrigin"):
            self.initOrigin()
        if hasattr(self, "initProperties"):
            self.initProperties(bare)
        if hasattr(self, "onSettingsChange"):
            hub.settings.changed.connect(self.onSettingsChange)

    def __hash__(self):
        return hash(self.uuid)

    def __eq__(self, other):
        if not isinstance(other, ElementMixin):
            return NotImplemented
        return self.uuid == other.uuid

    def resetUuid(self : Self) -> None:
        self.uuid = str(uuid.uuid4())

class ElementBoundShapeMixin:
    # instance attributes
    _brect  : QRectF       # bounding rect
    _hshape : QPainterPath # hit detect shape

    def initBoundShape(self : Self) -> None:
        self._brect  = QRectF()
        self._hshape = QPainterPath()

    def boundingRect(self : Self) -> QRectF:
        return self._brect

    def shape(self : Self) -> QPainterPath:
        return self._hshape

class ElementPosMixin:
    _PROPERTY_SPECS_POS = {
        "Position X" : PropertySpec(
            type_name = "float",
            getter    = lambda self: self.pos().x(),
            setter    = lambda self, value: self.setPosX(value)
        ),
        "Position Y" : PropertySpec(
            type_name = "float",
            getter    = lambda self: self.pos().y(),
            setter    = lambda self, value: self.setPosY(value)
        )
    }

    def moveBy(self : Self, offset : QPointF) -> None:
        super().moveBy(offset.x(), offset.y())

    def setPosX(self : Self, value : float) -> None:
        pos = self.pos()
        pos.setX(value)
        self.setPos(pos)

    def setPosY(self : Self, value : float) -> None:
        pos = self.pos()
        pos.setY(value)
        self.setPos(pos)

class ElementLocMixin:
    # instance attributes
    _loc : EdgeLoc

    _PROPERTY_SPECS_LOC = {
        "Location" : PropertySpec(
            type_name = "EdgeLoc",
            getter    = lambda self: self.loc(),
            setter    = lambda self, value: self.setLoc(value)
        )
    }

    def loc(self : Self) -> EdgeLoc:
        return self._loc

    def setLoc(self : Self, loc : EdgeLoc) -> None:
        self._loc = loc
        self.prepareGeometryChange()
        match loc.edge:
            case Edge.LEFT:   self.setRotation(0)
            case Edge.RIGHT:  self.setRotation(180)
            case Edge.TOP:    self.setRotation(90)
            case Edge.BOTTOM: self.setRotation(270)
        if hasattr(self, "_name_text"):
            name_centre = QPointF(self._name_text.boundingRect().center())
            self._name_text.setTransformOriginPoint(name_centre)
            match loc.edge:
                case Edge.LEFT:   self._name_text.setRotation(0)
                case Edge.RIGHT:  self._name_text.setRotation(180)
                case Edge.TOP:    self._name_text.setRotation(180)
                case Edge.BOTTOM: self._name_text.setRotation(0)
        parent : "PinRect" = self.parentItem()
        edge_pos = parent.getEdgeLocPos(loc) if parent else QPointF()
        super().setPos(edge_pos)

    def setLocPos(
        self : Self,
        pos  : QPointF,
        snap : Optional[QPointF] = None
    ) -> None:
        parent : "PinRect" = self.parentItem()
        self.setLoc(parent.getEdgeLoc(pos, snap))

    def pos(self : Self) -> QPointF:
        raise NotImplementedError("pos is not implemented for ElementLocMixin")

    def setPos(self : Self, pos : QPointF) -> None:
        raise NotImplementedError("setPos is not implemented for ElementLocMixin")

class ElementAnchorPointsMixin:
    # instance attributes
    _anchor_points : dict[str, "AnchorPoint"]

class ElementRectAnchorPointsMixin(ElementAnchorPointsMixin):
    # class variables
    _ANCHOR_POINTS = {
        "Top Left"      : ( 0.0 , 0.0 ),
        "Top Center"    : ( 0.5 , 0.0 ),
        "Top Right"     : ( 1.0 , 0.0 ),
        "Center Left"   : ( 0.0 , 0.5 ),
        "Center"        : ( 0.5 , 0.5 ),
        "Center Right"  : ( 1.0 , 0.5 ),
        "Bottom Left"   : ( 0.0 , 1.0 ),
        "Bottom Center" : ( 0.5 , 1.0 ),
        "Bottom Right"  : ( 1.0 , 1.0 )
    }
    _AP_TYPES : dict[str, APType]

    # instance attributes
    _rect   : QRectF   # border rectangle, maintained by element

    def initAnchorPoints(self : Self) -> None:
        self._anchor_points = {}
        for ap_name, ap_type in self._AP_TYPES.items():
            self._anchor_points[ap_name] = AnchorPoint(
                name   = ap_name,
                type   = ap_type,
                parent = self
            )

    def updateKeypoints(self : Self) -> None:
        for name, (x, y) in self._ANCHOR_POINTS.items():
            self._anchor_points[name].setPos(QPointF(
                x * self._rect.width(),
                y * self._rect.height()
            ))

    def updateHandlesVisibility(self : Self) -> None:
        for ap in self._anchor_points.values():
            ap._handle.setVisible(self.isSelected())

class ElementOriginMixin:
    # class variables
    _PROPERTY_SPECS_ORIGIN = {
        "Origin" : PropertySpec(
            getter    = lambda self: self.getOrigin(),
            setter    = lambda self, value: self.setOrigin(value)
        )
    }

    # instance attributes
    _pos    : QPointF        # position of origin w.r.t. scene/parent
    _origin : "AnchorPoint"  # origin anchor point

    def initOrigin(self : Self) -> None:
        self._pos = super().pos()
        self._origin = next(iter(self._anchor_points.values()))
        self._origin._handle.onOriginChange(True)
        self.updateOrigin()

    def pos(self : Self) -> QPointF:
        return super().pos() + self._origin.pos()

    def setPos(self : Self, pos : QPointF) -> None:
        self._pos = pos
        super().setPos(pos - self._origin.pos())

    def getOrigin(self : Self) -> str:
        return self._origin._name

    def setOrigin(self, name : str) -> None:
        self._origin._handle.onOriginChange(False)
        self._origin = self._anchor_points[name]
        self._origin._handle.onOriginChange(True)
        self.setPos(self.pos())

    def updateOrigin(self : Self) -> None:
        """Reposition following possible movement of origin anchor point."""
        self.setPos(self._pos)

class ElementLineMixin:
    _CAP_STYLE  = Qt.PenCapStyle.SquareCap
    _JOIN_STYLE = Qt.PenJoinStyle.MiterJoin
    _PROPERTY_SPECS_LINE = {
        "Line Color" : PropertySpec(
            type_name = "QColor",
            exists    = lambda self: self.line is not None,
            getter    = lambda self: self.line.getColor(),
            setter    = lambda self, value: self.line.setColor(value)
        ),
        "Line Width" : PropertySpec(
            type_name = "float",
            exists    = lambda self: self.line is not None,
            getter    = lambda self: self.line.getWidth(),
            setter    = lambda self, value: self.line.setWidth(value)
        ),
        "Line Style" : PropertySpec(
            type_name = "PenStyle",
            exists    = lambda self: self.line is not None,
            getter    = lambda self: self.line.getStyle(),
            setter    = lambda self, value: self.line.setStyle(value)
        )
    }

    line : Line

    def initLine(self : Self):
        self.line = Line(self)

class ElementFillMixin:
    _PROPERTY_SPECS_FILL = {
        "Fill Color" : PropertySpec(
            type_name = "QColor",
            exists    = lambda self: self.fill is not None,
            getter    = lambda self: self.fill.getColor(),
            setter    = lambda self, value: self.fill.setColor(value)
        ),
        "Fill Style" : PropertySpec(
            type_name = "BrushStyle",
            exists    = lambda self: self.fill is not None,
            getter    = lambda self: self.fill.getStyle(),
            setter    = lambda self, value: self.fill.setStyle(value)
        )
    }

    fill : Fill

    def initFill(self : Self):
        self.fill = Fill(self)

class ElementQuillMixin:
    _PROPERTY_SPECS_QUILL = {
        "Text Color" : PropertySpec(
            type_name = "QColor",
            exists    = lambda self: self.quill is not None,
            getter    = lambda self: self.quill.getColor(),
            setter    = lambda self, value: self.quill.setColor(value)
        ),
        "Text Font" : PropertySpec(
            type_name = "str",
            exists    = lambda self: self.quill is not None,
            getter    = lambda self: self.quill.getFamily(),
            setter    = lambda self, value: self.quill.setFamily(value)
        ),
        "Text Size" : PropertySpec(
            type_name = "float",
            exists    = lambda self: self.quill is not None,
            getter    = lambda self: self.quill.getSize(),
            setter    = lambda self, value: self.quill.setSize(value)
        ),
        "Text Bold" : PropertySpec(
            type_name = "bool",
            exists    = lambda self: self.quill is not None,
            getter    = lambda self: self.quill.getBold(),
            setter    = lambda self, value: self.quill.setBold(value)
        ),
        "Text Italic" : PropertySpec(
            type_name = "bool",
            exists    = lambda self: self.quill is not None,
            getter    = lambda self: self.quill.getItalic(),
            setter    = lambda self, value: self.quill.setItalic(value)
        ),
        "Text Underline" : PropertySpec(
            type_name = "bool",
            exists    = lambda self: self.quill is not None,
            getter    = lambda self: self.quill.getUnderline(),
            setter    = lambda self, value: self.quill.setUnderline(value)
        )
    }

    quill : Quill

    def initQuill(self : Self):
        self.quill = Quill(self)

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
                if hasattr(self, "line"):
                    self.line.onSelectionChange(value)
                if hasattr(self, "fill"):
                    self.fill.onSelectionChange(value)
                if hasattr(self, "quill"):
                    self.quill.onSelectionChange(value)
                if hasattr(self, "updateHandlesVisibility"):
                    self.updateHandlesVisibility()
                if hasattr(self, "onSelectionChange"):
                    self.onSelectionChange(value)
        return super().itemChange(change, value)

    def onSettingsChange(self : Self) -> None:
        self.prepareGeometryChange()
        if hasattr(self, "line"):
            self.line.onSettingsChange()
        if hasattr(self, "fill"):
            self.fill.onSettingsChange()
        if hasattr(self, "quill"):
            self.quill.onSettingsChange()
        if hasattr(self, "outline"):
            self.outline.onSettingsChange()
        self.onGeometryChange()

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

class ElementCloneMixin:
    def clone(self : Self, original : Optional[Self] = None) -> Self:
        """Create a clone of this element with a new UUID."""
        source = original if original is not None else self
        clone = self.__class__(bare=True)
        # clone properties
        if hasattr(self, "_properties"):
            clone._properties = self._properties.copy()
            for pn in clone._properties:
                clone_ps = clone._properties[pn]
                source_ps = source._properties[pn]
                if isinstance(clone_ps, PropertySpec):
                    clone_ps.setter(clone, source_ps.getter(source))
                else:
                    clone_ps.value = source_ps.value
        # clone property texts and pins
        from .port_pin import BasePin
        for source_child in source.childItems():
            if isinstance(source_child, BasePin):
                clone_pin = source_child.clone(source_child) # TODO is passing item needed?
                clone_pin.setParentItem(clone)
            elif isinstance(source_child, AnchorPoint):
                for source_ap_child in source_child.childItems():
                    if isinstance(source_ap_child, PropertyText):
                        clone_ap_child = source_ap_child.clone(source_ap_child)
                        clone_ap_child.setParentItem(
                            clone._anchor_points[source_child.getLoc()]
                        )
        return clone

class ElementXmlMixin:
    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        xw.writeStartElement(self.__class__.__name__)
        toXmlAttrs(self, xw)
        from .port_pin import BasePin
        for child in self.childItems():
            if isinstance(child, PropertyText | BasePin):
                child.toXml(xw)
        xw.writeEndElement()

    @classmethod
    def fromXml(cls : Self, xr: QXmlStreamReader) -> Self:
        instance = cls(bare=True)
        fromXmlAttrs(instance, xr)
        instance.onGeometryChange()
        # check if we're already at the end element (self-closing)
        if xr.isEndElement() and xr.name() == cls.__name__:
            return instance
        # read child PropertyText and pin elements
        while not (xr.isEndElement() and xr.name() == cls.__name__):
            if xr.isStartElement():
                if xr.name() == "BlockPin":
                    child = BlockPin.fromXml(xr)
                    child.setParentItem(instance)
                elif xr.name() == "PropertyText":
                    child : PropertyText = PropertyText.fromXml(xr)
                    child.setParentItem(instance._anchor_points[child._origin()])
                else:
                    logger.warning(f"Unexpected child element: {xr.name()}")
                    continue
            xr.readNext()
        return instance



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
    "APType",
    "Edge",
    "EdgeLoc",
    "SignalDirection",
    "RangeDirection",
    "VectorRange",
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
    "clone"
]
from .anchor_point import AnchorPoint
__all__ += anchor_point.__all__
from .tether_text import TetherText, Tether
__all__ += tether_text.__all__
from .property_text import PropertyDisplay, PropertyTextSpec, PropertyText
__all__ += property_text.__all__
from .text import Text
__all__ += text.__all__
from .text_block import TextBlock
__all__ += text_block.__all__
from .rectangle import Rectangle
__all__ += rectangle.__all__
from .port_pin import Port, BlockPin
__all__ += port_pin.__all__
from .pin_rect import PinRect
__all__ += pin_rect.__all__
from .block import Block
__all__ += block.__all__
from .symbol_instance import SymbolInstance
__all__ += symbol_instance.__all__

element_class_dict = {}
for class_name in __all__:
    element_class_dict[class_name] = globals()[class_name]
__all__ += ["element_class_dict"]
