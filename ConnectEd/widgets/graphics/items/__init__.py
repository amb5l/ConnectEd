from typing      import Self
from dataclasses import dataclass
from enum        import Enum

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtGui     import QColor

from ....app import logger

from ....core.utils import registerClass

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


class RangeDirection(Enum):
    NONE = ":"
    DOWN = "\u25bc"
    UP   = "\u25b2"


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
registerClass( _item_classes , "Ellipse"                             )
registerClass( _item_classes , "Polyline"                            )
registerClass( _item_classes , "TextLine"          , "text"          )
registerClass( _item_classes , "TextBlock"         , "text"          )
