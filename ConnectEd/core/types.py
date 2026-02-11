from typing      import Self
from dataclasses import dataclass
from enum        import Enum, StrEnum

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QGraphicsItem

from ..widgets.graphics.items import ItemMixin


class Default:
    def __str__(self : Self) -> str: return "default"
    def __repr__(self : Self) -> str: return "<default>"

DEFAULT = Default()


class NoChange:
    def __str__(self : Self): return "no change"
    def __repr__(self : Self): return "<no change>"

NO_CHANGE = NoChange()


class AlignMixin:
    def toStr(self : Self) -> str:
        return self.name

    @classmethod
    def fromStr(cls, s : str) -> Self:
        return cls[s]


class AlignH(AlignMixin, Enum):
    LEFT   = Qt.AlignmentFlag.AlignLeft
    CENTER = Qt.AlignmentFlag.AlignHCenter
    RIGHT  = Qt.AlignmentFlag.AlignRight


class AlignV(AlignMixin,Enum):
    TOP    = Qt.AlignmentFlag.AlignTop
    MIDDLE = Qt.AlignmentFlag.AlignVCenter
    BOTTOM = Qt.AlignmentFlag.AlignBottom


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


@dataclass
class Text:
    string : str   # text string value
    block  : bool  # False = line, True = block

    def __str__(self) -> str:
        return self.string


class HandleId(StrEnum):
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


class BlockPinHandleId(HandleId):
    ENTRY = "Entry"  # also placement origin
    NAME  = "Name"   # set just in from signal direction shape


class SymbolPinHandleId(HandleId):
    ORIGIN = "Origin"  # placement origin
    ENTRY  = "Entry"   # tip of external pin shape
    NAME   = "Name"    # set just in from placement origin


LineWidth = float | Default
PenStyle = Qt.PenStyle | Default
BrushStyle = Qt.BrushStyle | Default
FontFamily = str | Default
FontSize = float | Default
