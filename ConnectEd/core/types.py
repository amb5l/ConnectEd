from typing      import Self
from dataclasses import dataclass
from enum        import Enum, StrEnum

from PyQt6.QtCore    import Qt
from PyQt6.QtGui     import QColor


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
class Direction(Enum):
    NONE = None
    IN   = "in"
    OUT  = "out"
    BI   = "bi"


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
    ENTRY = "Entry"  # also placement origin
    NAME  = "Name"   # set beside signal direction shape


class BlockPinHandleId(HandleId):
    ENTRY = "Entry"  # also placement origin
    NAME  = "Name"   # set just in from signal direction shape


class SymbolPinHandleId(HandleId):
    ORIGIN = "Origin"  # placement origin
    ENTRY  = "Entry"   # tip of external pin shape
    NAME   = "Name"    # set just in from placement origin

class PropertyDisplay(Enum):
    NONE = "<none>"
    SHOW = "Show"
    HIDE = "Hide"


Color = QColor | Default | NoChange
LineWidth = float | Default
PenStyle = Qt.PenStyle | Default
BrushStyle = Qt.BrushStyle | Default
FontFamily = str | Default
FontSize = float | Default


_DATA_KIND_TYPES: dict["DataKind", tuple[type, ...]] = {}
_DATA_KIND_EDITORS: dict["DataKind", type] = {}


def _populate_data_kind_maps() -> None:
    from ..widgets.dialogs.components.edit import \
        StrEditor, TextEditor, IntEditor, FloatEditor, BoolEditor
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
        DataKind.STR               : (str,),
        DataKind.TEXT              : (str,),
        DataKind.INT               : (int,),
        DataKind.FLOAT             : (float,),
        DataKind.BOOL              : (bool,),
        DataKind.DISPLAY           : (PropertyDisplay,),
        DataKind.RECT_HANDLE       : (RectHandleId,),
        DataKind.LINE_HANDLE       : (LineHandleId,),
        DataKind.BLOCK_PIN_HANDLE  : (BlockPinHandleId,),
        DataKind.SYMBOL_PIN_HANDLE : (SymbolPinHandleId,),
        DataKind.ROTATION          : (float,),
        DataKind.ALIGN_H           : (AlignH,),
        DataKind.ALIGN_V           : (AlignV,),
        DataKind.EDGE              : (Edge,),
        DataKind.DIRECTION         : (Direction,),
        DataKind.COLOR             : (QColor, Default),
        DataKind.PEN_STYLE         : (Qt.PenStyle, Default),
        DataKind.PEN_WIDTH         : (float, Default),
        DataKind.BRUSH_STYLE       : (Qt.BrushStyle, Default),
        DataKind.FONT_FAMILY       : (str, Default),
        DataKind.FONT_SIZE         : (float, Default),
        DataKind.FONT_BOOL         : (bool, Default)
    })
    _DATA_KIND_EDITORS.update({
        DataKind.STR               : StrEditor,
        DataKind.TEXT              : TextEditor,
        DataKind.INT               : IntEditor,
        DataKind.FLOAT             : FloatEditor,
        DataKind.BOOL              : BoolEditor,
        DataKind.DISPLAY           : EnumComboBox[PropertyDisplay],
        DataKind.RECT_HANDLE       : EnumComboBox[RectHandleId],
        DataKind.LINE_HANDLE       : EnumComboBox[LineHandleId],
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
    STR               = "String"
    TEXT              = "Text"
    INT               = "Integer"
    FLOAT             = "Float"
    BOOL              = "Boolean"
    DISPLAY           = "Display"
    RECT_HANDLE       = "Rectangle Handle"
    LINE_HANDLE       = "Line Handle"
    BLOCK_PIN_HANDLE  = "Block Pin Handle"
    SYMBOL_PIN_HANDLE = "Symbol Pin Handle"
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

    @property
    def types(self : Self) -> tuple[type, ...]:
        if not _DATA_KIND_TYPES:
            _populate_data_kind_maps()
        return _DATA_KIND_TYPES[self]

    @property
    def editor(self : Self) -> type:
        if not _DATA_KIND_EDITORS:
            _populate_data_kind_maps()
        return _DATA_KIND_EDITORS[self]
