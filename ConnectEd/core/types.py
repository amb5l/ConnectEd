from typing      import Self
from types       import NoneType
from dataclasses import dataclass
from enum        import Enum, StrEnum

from PyQt6.QtCore    import Qt
from PyQt6.QtGui     import QColor

from .check import checked


class NoChange:
    def __eq__(self : Self, other : object) -> bool:
        return isinstance(other, NoChange)

    def __hash__(self : Self) -> int:
        return hash(NoChange)

    def __copy__(self : Self) -> "NoChange":
        return NO_CHANGE

    def __deepcopy__(self : Self, _memo : object) -> "NoChange":
        return NO_CHANGE

    def __str__(self : Self) -> str:
        return "no change"

    def __repr__(self : Self) -> str:
        return "<no change>"


NO_CHANGE = NoChange()


class EnDis(Enum):
    DISABLE = False
    ENABLE  = True


class Axis(StrEnum):
    H = "H"
    V = "V"

    def __invert__(self : Self) -> Self:
        return Axis.H if self == Axis.V else Axis.V

class Polarity(StrEnum):
    POS = "Positive"
    NEG = "Negative"

    def __invert__(self : Self) -> Self:
        return Polarity.POS if self == Polarity.NEG else Polarity.NEG


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


class Display(Enum):
    NONE = "<none>"
    SHOW = "Show"
    HIDE = "Hide"


_DATA_KIND_TYPES: dict["DataKind", tuple[type, ...]] = {}
_DATA_KIND_EDITORS: dict["DataKind", type] = {}


def _populate_data_kind_maps() -> None:
    from ..widgets.dialogs.components.edit import \
        StrEditor, TextEditor, IntEditor, FloatEditor, SizeEditor, BoolEditor
    from ..widgets.dialogs.components.combo.enum        import EnumComboBox
    from ..widgets.dialogs.components.combo.rotation    import RotationComboBox
    from ..widgets.dialogs.components.combo.color       import ColorComboBox
    from ..widgets.dialogs.components.combo.line_width  import LineWidthComboBox
    from ..widgets.dialogs.components.combo.line_style  import LineStyleComboBox
    from ..widgets.dialogs.components.combo.fill_style  import FillStyleComboBox
    from ..widgets.dialogs.components.combo.font_family import FontFamilyComboBox
    from ..widgets.dialogs.components.combo.font_size   import FontSizeComboBox
    from ..widgets.dialogs.components.combo.font_bool   import FontBoolComboBox

    _DATA_KIND_TYPES.update({
        DataKind.KIND              : (DataKind,),
        DataKind.STR               : (str,),
        DataKind.TEXT              : (str,),
        DataKind.INT               : (int,),
        DataKind.FLOAT             : (float,),
        DataKind.SIZE              : (float, NoneType),
        DataKind.BOOL              : (bool,),
        DataKind.EN_DIS            : (EnDis,),
        DataKind.DISPLAY           : (Display,),
        DataKind.RECT_HANDLE       : (RectHandleId,),
        DataKind.LINE_HANDLE       : (LineHandleId,),
        DataKind.PORT_HANDLE       : (PortHandleId,),
        DataKind.BLOCK_PIN_HANDLE  : (BlockPinHandleId,),
        DataKind.SYMBOL_PIN_HANDLE : (SymbolPinHandleId,),
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
    _DATA_KIND_EDITORS.update({
        DataKind.KIND              : EnumComboBox[DataKind],
        DataKind.STR               : StrEditor,
        DataKind.TEXT              : TextEditor,
        DataKind.INT               : IntEditor,
        DataKind.FLOAT             : FloatEditor,
        DataKind.SIZE              : SizeEditor,
        DataKind.BOOL              : BoolEditor,
        DataKind.EN_DIS            : EnumComboBox[EnDis],
        DataKind.DISPLAY           : EnumComboBox[Display],
        DataKind.RECT_HANDLE       : EnumComboBox[RectHandleId],
        DataKind.LINE_HANDLE       : EnumComboBox[LineHandleId],
        DataKind.PORT_HANDLE       : EnumComboBox[PortHandleId],
        DataKind.BLOCK_PIN_HANDLE  : EnumComboBox[BlockPinHandleId],
        DataKind.SYMBOL_PIN_HANDLE : EnumComboBox[SymbolPinHandleId],
        DataKind.ROTATION          : RotationComboBox,
        DataKind.ALIGN_H           : EnumComboBox[AlignH],
        DataKind.ALIGN_V           : EnumComboBox[AlignV],
        DataKind.EDGE              : EnumComboBox[Edge],
        DataKind.DIRECTION         : EnumComboBox[Direction],
        DataKind.COLOR             : ColorComboBox,
        DataKind.PEN_STYLE         : LineStyleComboBox,
        DataKind.PEN_WIDTH         : LineWidthComboBox,
        DataKind.BRUSH_STYLE       : FillStyleComboBox,
        DataKind.FONT_FAMILY       : FontFamilyComboBox,
        DataKind.FONT_SIZE         : FontSizeComboBox,
        DataKind.FONT_BOOL         : FontBoolComboBox
    })


class DataKind(StrEnum):
    KIND              = "Kind"
    STR               = "String"
    TEXT              = "Text"
    INT               = "Integer"
    FLOAT             = "Float"
    SIZE              = "Size"
    BOOL              = "Boolean"
    EN_DIS            = "Enable"
    DISPLAY           = "Display"
    RECT_HANDLE       = "Rectangle Handle"
    LINE_HANDLE       = "Line Handle"
    PORT_HANDLE       = "Port Handle"
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
            _populate_data_kind_maps()
        return _DATA_KIND_TYPES[self]

    def editor(self : Self) -> type:
        if not _DATA_KIND_EDITORS:
            _populate_data_kind_maps()
        return _DATA_KIND_EDITORS[self]


class Counter:
    @checked
    def __init__(self : Self) -> None:
        self._count = -1

    @checked
    def next(self : Self) -> int:
        self._count += 1
        return self._count
