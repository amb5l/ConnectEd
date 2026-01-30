from typing      import Self
from dataclasses import dataclass
from enum        import Enum

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QGraphicsItem

from ....app import logger

from ....core.utils import registerClass

from .mixin import ItemMixin


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
registerClass( _item_classes , "ConnSegItem"               )
registerClass( _item_classes , "PortItem"                  )
registerClass( _item_classes , "BufGateItem"      , "gate" )
registerClass( _item_classes , "AndGateItem"      , "gate" )
registerClass( _item_classes , "OrGateItem"       , "gate" )
registerClass( _item_classes , "XorGateItem"      , "gate" )
registerClass( _item_classes , "BlockItem"                 )
registerClass( _item_classes , "PropertyTextItem"          )
registerClass( _item_classes , "SymbolPinItem"             )
registerClass( _item_classes , "LineItem"                  )
registerClass( _item_classes , "RectangleItem"             )
registerClass( _item_classes , "EllipseItem"               )
registerClass( _item_classes , "PolylineItem"              )
registerClass( _item_classes , "TextItem"                  )
