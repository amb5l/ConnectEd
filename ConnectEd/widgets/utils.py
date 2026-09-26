from __future__ import annotations

from ..core.check                            import checked
from ..core.types                            import (
    DataKind, AlignH, AlignV, Edge, Direction,
    RectHandleId, LineHandleId, PortHandleId,
    GatePinHandleId, BlockPinHandleId, SymbolPinHandleId, TapHandleId,
)

from .dialogs.components.edit                import (
    StrEditor, TextEditor, IntEditor, FloatEditor, SizeEditor, BoolEditor,
)

from .dialogs.components.check_box.font_bool import FontBoolCheckBox
from .dialogs.components.combo.enum          import EnumComboBox
from .dialogs.components.combo.rotation      import RotationComboBox
from .dialogs.components.combo.color         import ColorComboBox
from .dialogs.components.combo.line_width    import LineWidthComboBox
from .dialogs.components.combo.line_style    import LineStyleComboBox
from .dialogs.components.combo.fill_style    import FillStyleComboBox
from .dialogs.components.combo.font_family   import FontFamilyComboBox
from .dialogs.components.combo.font_size     import FontSizeComboBox
from .dialogs.components.combo.font_bool     import FontBoolComboBox


_KIND_DIALOG_EDITORS : dict[DataKind, type] = {
    DataKind.KIND              : EnumComboBox[DataKind],
    DataKind.STR               : StrEditor,
    DataKind.TEXT              : TextEditor,
    DataKind.INT               : IntEditor,
    DataKind.FLOAT             : FloatEditor,
    DataKind.SIZE              : SizeEditor,
    DataKind.BOOL              : BoolEditor,
    DataKind.RECT_HANDLE       : EnumComboBox[RectHandleId],
    DataKind.LINE_HANDLE       : EnumComboBox[LineHandleId],
    DataKind.PORT_HANDLE       : EnumComboBox[PortHandleId],
    DataKind.GATE_PIN_HANDLE   : EnumComboBox[GatePinHandleId],
    DataKind.BLOCK_PIN_HANDLE  : EnumComboBox[BlockPinHandleId],
    DataKind.SYMBOL_PIN_HANDLE : EnumComboBox[SymbolPinHandleId],
    DataKind.TAP_HANDLE        : EnumComboBox[TapHandleId],
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
}


for kind in DataKind:
    if kind is not DataKind.DUMMY and kind not in _KIND_DIALOG_EDITORS:
        raise ValueError(f"No editor for kind: {kind}")


def kind2dialogEditor(kind : DataKind) -> type:
    return _KIND_DIALOG_EDITORS[kind]


_KIND_CELL_EDITORS : dict[DataKind, type] = {
    **_KIND_DIALOG_EDITORS,
    DataKind.FONT_BOOL : FontBoolCheckBox,
}


@checked
def kind2cellEditor(kind : DataKind) -> type:
    return _KIND_CELL_EDITORS[kind]
