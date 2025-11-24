from typing      import Self
from dataclasses import dataclass
from enum        import Enum

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtGui     import QColor

from ....app import logger

from ....core.utils import pascal2snake, registerClass

from .mixin import ItemMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .mixin.line  import Line
    from .mixin.fill  import Fill
    from .mixin.quill import Quill


ItemType = ItemMixin | QGraphicsItem


class Default:
    def __str__(self : Self): return "default"
    def __repr__(self : Self): return "<default>"

DEFAULT = Default()


class NoChange:
    def __str__(self : Self): return "no change"
    def __repr__(self : Self): return "<no change>"

NO_CHANGE = NoChange()


class Edge(Enum):
    UNDEFINED = "Undefined"
    LEFT      = "Left"
    BOTTOM    = "Bottom"
    RIGHT     = "Right"
    TOP       = "Top"


@dataclass
class EdgeLoc:
    edge   : Edge  | None = None
    offset : float | None = None

    def toStr(self : Self) -> str:
        return f"{self.edge.value},{self.offset}" \
              if self.edge is not None else "None"

    @classmethod
    def fromStr(cls, s : str) -> Self:
        edge, offset = s.split(",")
        return cls(Edge(edge), float(offset))


# TODO: consider passive, 3-state etc for EE schematics
class SignalDirection(Enum):
    NONE = None
    IN   = "in"
    OUT  = "out"
    BI   = "bi"


class RangeDirection(Enum):
    NONE = ":"
    DOWN = "\u25bc"
    UP   = "\u25b2"


class VectorRange:
    left  : str            # left value (may refer to parameter/generic)
    dir   : RangeDirection # down or up
    right : str            # right value (may refer to parameter/generic)

    def __init__(self : Self, left : str, dir : RangeDirection, right : str) -> None:
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

    def toStr(self : Self):
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
    color : Default | QColor      | None = None
    width : Default | float       | None = None
    style : Default | Qt.PenStyle | None = None


@dataclass
class LinePrefChange:
    color : NoChange | Default | QColor      | None = None
    width : NoChange | Default | float       | None = None
    style : NoChange | Default | Qt.PenStyle | None = None


@dataclass
class FillSpec:
    color : QColor
    style : Qt.BrushStyle


@dataclass
class FillPref:
    color : Default | QColor        = DEFAULT
    style : Default | Qt.BrushStyle = DEFAULT

    def toStr(self : Self):
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
    color : Default | QColor        | None = None
    style : Default | Qt.BrushStyle | None = None


@dataclass
class FillPrefChange:
    color : NoChange | Default | QColor        | None = None
    style : NoChange | Default | Qt.BrushStyle | None = None


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

    def toStr(self : Self):
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
    color     : Default | QColor | None = None
    family    : Default | str    | None = None
    size      : Default | float  | None = None
    bold      : Default | bool   | None = None
    italic    : Default | bool   | None = None
    underline : Default | bool   | None = None


@dataclass
class QuillPrefChange:
    color     : NoChange | Default | QColor | None = None
    family    : NoChange | Default | str    | None = None
    size      : NoChange | Default | float  | None = None
    bold      : NoChange | Default | bool   | None = None
    italic    : NoChange | Default | bool   | None = None
    underline : NoChange | Default | bool   | None = None


@dataclass
class Appearance:
    line  : "Line  | None" = None
    fill  : "Fill  | None" = None
    quill : "Quill | None" = None


@dataclass
class AppearanceSpec:
    line  : LineSpec  | None = None
    fill  : FillSpec  | None = None
    quill : QuillSpec | None = None


@dataclass
class AppearancePref:
    line  : LinePref  | None = None
    fill  : FillPref  | None = None
    quill : QuillPref | None = None


@dataclass
class AppearancePrefChange:
    line  : LinePrefChange  | None = None
    fill  : FillPrefChange  | None = None
    quill : QuillPrefChange | None = None


def clone(items : list[ItemMixin]) -> list[ItemMixin]:
    r = []
    for item in items:
        try:
            r.append(item.clone())
        except Exception as e:
            logger().warning(f"Failed to clone item {item}: {e}")
    return r


_item_classes = {}
registerClass( _item_classes , "ConnSeg"                             )
registerClass( _item_classes , "Port"                                )
registerClass( _item_classes , "BufGate"           , "gate"          )
registerClass( _item_classes , "AndGate"           , "gate"          )
registerClass( _item_classes , "OrGate"            , "gate"          )
registerClass( _item_classes , "XorGate"           , "gate"          )
registerClass( _item_classes , "Block"                               )
registerClass( _item_classes , "PropertyTextLine"  , "property_text" )
registerClass( _item_classes , "PropertyTextBlock" , "property_text" )
registerClass( _item_classes , "SymbolPin"                           )
registerClass( _item_classes , "Line"                                )
registerClass( _item_classes , "Rectangle"                           )
registerClass( _item_classes , "Polyline"                            )
registerClass( _item_classes , "TextLine"                            )
registerClass( _item_classes , "TextBlock"                           )
