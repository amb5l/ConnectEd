from typing import Self, Any

from PyQt6.QtCore import Qt
from PyQt6.QtGui  import QColor, QStandardItem

from ....app import logger

from ....core.check import checked
from ....core.types import Default, AlignH, AlignV, Edge, Direction, \
                           RectHandleId, LineHandleId, \
                           BlockPinHandleId, SymbolPinHandleId
from ....core.utils import val2str, trace

from ...graphics.properties import PropertyDisplay


class PropertiesItem(QStandardItem):
    _KIND_MAP = {
        "Color"      : "QColor | Default",
        "LineWidth"  : "float | Default",
        "PenStyle"   : "Qt.PenStyle | Default",
        "BrushStyle" : "Qt.BrushStyle | Default",
        "FontSize"   : "float | Default",
        "FontFamily" : "str | Default",
        "FontBool"   : "bool | Default"
    }
    _TYPE_MAP = {
        "str"               : str,
        "float"             : float,
        "bool"              : bool,
        "Default"           : Default,
        "Display"           : PropertyDisplay,
        "AlignH"            : AlignH,
        "AlignV"            : AlignV,
        "Edge"              : Edge,
        "Direction"         : Direction,
        "QColor"            : QColor,
        "Qt.PenStyle"       : Qt.PenStyle,
        "Qt.BrushStyle"     : Qt.BrushStyle,
        "RectHandleId"      : RectHandleId,
        "LineHandleId"      : LineHandleId,
        "BlockPinHandleId"  : BlockPinHandleId,
        "SymbolPinHandleId" : SymbolPinHandleId
    }
    _IDX_KIND    = 0
    _IDX_TYPES   = 1
    _IDX_INITIAL = 2
    _IDX_CURRENT = 3
    _IDX_DEFAULT = 4

    @checked
    def __init__(
        self     : Self,
        kind     : str,
        value    : Any,           # None if existing
        default  : Any  = None,   # None if default not applicable
        new      : bool = False,
        editable : bool = True,
        enabled  : bool = True
    ) -> None:
        super().__init__()
        self.setKind(kind)
        self.setInitial(None if new else value)
        self.setValue(value)
        self.setDefault(default)
        self.setEnabled(enabled)
        self.setEditable(editable)

    @checked
    def setEnabled(self : Self, enabled : bool) -> None:
        super().setEnabled(enabled)
        self.setText(val2str(self.value()) if enabled else "")

    @checked
    def kind(self : Self) -> str:
        return self.data(Qt.ItemDataRole.UserRole + self._IDX_KIND)

    @checked
    def setKind(self : Self, kind : str) -> None:
        self.setData(kind, Qt.ItemDataRole.UserRole + self._IDX_KIND)
        # replace kinds with type hints
        for map_kind, map_hint in self._KIND_MAP.items():
            if map_kind in kind:
                kind = kind.replace(map_kind, map_hint)
        # convert type hint string to list of types
        type_list = []
        for type_name in kind.replace(" ", "").split("|"):
            # convert type name to type
            if type_name in self._TYPE_MAP:
                type_list.append(self._TYPE_MAP[type_name])
            else:
                logger().error(f"Invalid type name: {type_name}")
        self.setData(tuple(type_list), Qt.ItemDataRole.UserRole + self._IDX_TYPES)

    @checked
    def types(self : Self) -> tuple[type, ...]:
        return self.data(Qt.ItemDataRole.UserRole + self._IDX_TYPES)

    @checked
    def initial(self : Self) -> Any:
        return self.data(Qt.ItemDataRole.UserRole + self._IDX_INITIAL)

    @checked
    def setInitial(self : Self, value : Any) -> None:
        if not isinstance(value, self.types() + (type(None),)):  # None is allowed
            logger().error(f"Initial value {value} has invalid type: {type(value)}")
            trace(indent=True, args=True)
        else:
            self.setData(value, Qt.ItemDataRole.UserRole + self._IDX_INITIAL)

    @checked
    def value(self : Self) -> Any:
        return self.data(Qt.ItemDataRole.UserRole + self._IDX_CURRENT)

    @checked
    def setValue(self : Self, value : Any) -> None:
        if not isinstance(value, self.types()):
            logger().error(f"Value {value} has invalid type: {type(value)}")
        else:
            self.setData(value, Qt.ItemDataRole.UserRole + self._IDX_CURRENT)
            self.setText(val2str(value))

    @checked
    def default(self : Self) -> Any:
        return self.data(Qt.ItemDataRole.UserRole + self._IDX_DEFAULT)

    @checked
    def setDefault(self : Self, value : Any) -> None:
        self.setData(value, Qt.ItemDataRole.UserRole + self._IDX_DEFAULT)

    @checked
    def changed(self : Self) -> bool:
        return self.initial() != self.value()
