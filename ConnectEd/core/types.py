from __future__ import annotations

from typing          import Self, cast
from types           import NoneType
from collections.abc import Callable
from dataclasses     import dataclass
from enum            import Enum

from PyQt6.QtCore import Qt
from PyQt6.QtGui  import QColor

from .check import checked


class NoChange:
    def __eq__(self : Self, other : object) -> bool:
        return isinstance(other, NoChange)

    def __hash__(self : Self) -> int:
        return hash(NoChange)

    def __copy__(self : Self) -> NoChange:
        return NO_CHANGE

    def __deepcopy__(self : Self, _memo : object) -> NoChange:
        return NO_CHANGE

    def __str__(self : Self) -> str:
        return "no change"

    def __repr__(self : Self) -> str:
        return "<no change>"


NO_CHANGE = NoChange()


class Axis(Enum):
    H = "H"
    V = "V"

    def __invert__(self : Self) -> Axis:
        return Axis.H if self == Axis.V else Axis.V

class Polarity(Enum):
    POS = "Positive"
    NEG = "Negative"

    def __invert__(self : Self) -> Polarity:
        return Polarity.POS if self == Polarity.NEG else Polarity.NEG


class AlignMixin:
    def toStr(self : Self) -> str:
        if not isinstance(self, Enum):
            raise ValueError("Not an Enum")
        return self.name

    @classmethod
    def fromStr(cls : type[Self], s : str) -> Self:
        if not issubclass(cls, Enum):
            raise TypeError(f"{cls.__name__} is not an Enum subclass")
        return cast(Self, cls[s])


class AlignH(AlignMixin, Enum):
    LEFT   = Qt.AlignmentFlag.AlignLeft
    CENTER = Qt.AlignmentFlag.AlignHCenter
    RIGHT  = Qt.AlignmentFlag.AlignRight


class AlignV(AlignMixin, Enum):
    TOP    = Qt.AlignmentFlag.AlignTop
    MIDDLE = Qt.AlignmentFlag.AlignVCenter
    BOTTOM = Qt.AlignmentFlag.AlignBottom


class Edge(Enum):
    LEFT      = "Left"
    RIGHT     = "Right"
    TOP       = "Top"
    BOTTOM    = "Bottom"


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
class Direction(Enum):
    NONE = None
    IN   = "in"
    OUT  = "out"
    BI   = "bi"


class NetKind(Enum):
    UNRESOLVED = "unresolved"
    SCALAR     = "scalar"
    VECTOR     = "vector"


class HandleId(Enum):
    pass


class RectHandleId(HandleId):
    TOP_LEFT      = "Top Left"
    TOP_CENTER    = "Top Center"
    TOP_RIGHT     = "Top Right"
    MIDDLE_LEFT   = "Middle Left"
    MIDDLE_CENTER = "Middle Center"
    MIDDLE_RIGHT  = "Middle Right"
    BOTTOM_LEFT   = "Bottom Left"
    BOTTOM_CENTER = "Bottom Center"
    BOTTOM_RIGHT  = "Bottom Right"


class LineHandleId(HandleId):
    P1 = "P1"
    P2 = "P2"


class PortHandleId(HandleId):
    NODE = "Node"  # also placement origin
    NAME = "Name"  # set beside signal direction shape


class GatePinHandleId(HandleId):
    ORIGIN = "Origin"  # placement origin
    NODE   = "Node"  # tip of external pin shape
    NAME   = "Name"  # set beside signal direction shape


class BlockPinHandleId(HandleId):
    NODE = "Node"  # also placement origin
    NAME = "Name"  # set just in from signal direction shape


class SymbolPinHandleId(HandleId):
    ORIGIN = "Origin"  # placement origin
    NODE   = "Node"    # tip of external pin shape
    NAME   = "Name"    # set just in from placement origin


class TapHandleId(HandleId):
    SUFFIX = "Suffix"


_DATA_KIND_TYPES: dict[DataKind, tuple[type, ...]] = {}


def _populate_data_kind_types() -> None:
    _DATA_KIND_TYPES.update({
        DataKind.KIND              : (DataKind,),
        DataKind.STR               : (str,),
        DataKind.TEXT              : (str,),
        DataKind.INT               : (int,),
        DataKind.FLOAT             : (float,),
        DataKind.SIZE              : (float, NoneType),
        DataKind.BOOL              : (bool,),
        DataKind.RECT_HANDLE       : (RectHandleId,),
        DataKind.LINE_HANDLE       : (LineHandleId,),
        DataKind.PORT_HANDLE       : (PortHandleId,),
        DataKind.GATE_PIN_HANDLE   : (GatePinHandleId,),
        DataKind.BLOCK_PIN_HANDLE  : (BlockPinHandleId,),
        DataKind.SYMBOL_PIN_HANDLE : (SymbolPinHandleId,),
        DataKind.TAP_HANDLE        : (TapHandleId,),
        DataKind.ROTATION          : (float,),
        DataKind.ALIGN_H           : (AlignH,),
        DataKind.ALIGN_V           : (AlignV,),
        DataKind.EDGE              : (Edge,),
        DataKind.DIRECTION         : (Direction,),
        DataKind.COLOR             : (QColor, NoneType),
        DataKind.PEN_STYLE         : (Qt.PenStyle, NoneType),
        DataKind.PEN_WIDTH         : (float, NoneType),
        DataKind.BRUSH_STYLE       : (Qt.BrushStyle, NoneType),
        DataKind.FONT_FAMILY       : (str, NoneType),
        DataKind.FONT_SIZE         : (float, NoneType),
        DataKind.FONT_BOOL         : (bool, NoneType)
    })
    for kind in DataKind:
        if kind is not DataKind.DUMMY and kind not in _DATA_KIND_TYPES:
            raise ValueError(f"No type for kind: {kind}")


class DataKind(Enum):
    DUMMY             = "Dummy"
    KIND              = "Kind"
    STR               = "String"
    TEXT              = "Text"
    INT               = "Integer"
    FLOAT             = "Float"
    SIZE              = "Size"
    BOOL              = "Boolean"
    RECT_HANDLE       = "Rectangle Handle"
    LINE_HANDLE       = "Line Handle"
    PORT_HANDLE       = "Port Handle"
    GATE_PIN_HANDLE   = "Gate Pin Handle"
    BLOCK_PIN_HANDLE  = "Block Pin Handle"
    SYMBOL_PIN_HANDLE = "Symbol Pin Handle"
    TAP_HANDLE        = "Tap Handle"
    ROTATION          = "Rotation"
    ALIGN_H           = "Horizontal Alignment"
    ALIGN_V           = "Vertical Alignment"
    EDGE              = "Edge"
    DIRECTION         = "Direction"
    COLOR             = "Color"
    PEN_STYLE         = "Pen Style"
    PEN_WIDTH         = "Pen Width"
    BRUSH_STYLE       = "Brush Style"
    FONT_FAMILY       = "Font Family"
    FONT_SIZE         = "Font Size"
    FONT_BOOL         = "Font Boolean"

    def types(self : Self) -> tuple[type, ...]:
        if not _DATA_KIND_TYPES:
            _populate_data_kind_types()
        return _DATA_KIND_TYPES[self]


class Counter:
    @checked
    def __init__(self : Self) -> None:
        self._count = -1

    @checked
    def next(self : Self) -> int:
        self._count += 1
        return self._count


@dataclass(frozen=True)
class MenuSeparator:
    pass


@dataclass(frozen=True)
class MenuAction:
    label   : str
    handler : Callable[[], None]
    enabled : bool = True


@dataclass(frozen=True)
class MenuSub:
    label : str
    items : list[MenuEntry]


MenuEntry = MenuAction | MenuSub | MenuSeparator
