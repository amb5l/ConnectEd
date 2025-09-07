from typing      import Optional, Self
from dataclasses import dataclass
from enum        import Enum

from PyQt6.QtCore    import Qt
from PyQt6.QtGui     import QColor

from ....core.log import logger

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
    Cleat   = 0
    Mover   = 1
    Resizer = 2

class Edge(Enum):
    UNDEFINED = "Undefined"
    LEFT      = "Left"
    BOTTOM    = "Bottom"
    RIGHT     = "Right"
    TOP       = "Top"

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
