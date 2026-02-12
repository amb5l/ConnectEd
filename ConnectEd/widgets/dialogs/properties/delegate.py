from typing import Self, TypeAlias

from PyQt6.QtCore    import QModelIndex
from PyQt6.QtWidgets import QWidget, QStyledItemDelegate, QStyleOptionViewItem
from PyQt6.QtGui     import QStandardItemModel

from ....app import logger

from ....core.types import Edge, Direction, \
                           RectHandleId, LineHandleId, \
                           BlockPinHandleId, SymbolPinHandleId

from ...graphics.properties import PropertyDisplay

from ..components.edit import TextLineEditor, FloatEditor, BoolEditor, TextEditor

from ..components.combo.enum        import EnumComboBox
from ..components.combo.color       import ColorComboBox
from ..components.combo.line_width  import LineWidthComboBox
from ..components.combo.line_style  import LineStyleComboBox
from ..components.combo.fill_style  import FillStyleComboBox
from ..components.combo.font_family import FontFamilyComboBox
from ..components.combo.font_size   import FontSizeComboBox
from ..components.combo.font_bool   import FontBoolComboBox

from .item import PropertiesItem


EditorType : TypeAlias = \
    TextLineEditor                  | \
    FloatEditor                     | \
    BoolEditor                      | \
    TextEditor                      | \
    EnumComboBox[PropertyDisplay]   | \
    ColorComboBox                   | \
    LineWidthComboBox               | \
    LineStyleComboBox               | \
    FillStyleComboBox               | \
    FontFamilyComboBox              | \
    FontSizeComboBox                | \
    FontBoolComboBox                | \
    EnumComboBox[Edge]              | \
    EnumComboBox[Direction]         | \
    EnumComboBox[RectHandleId]      | \
    EnumComboBox[LineHandleId]      | \
    EnumComboBox[BlockPinHandleId]  | \
    EnumComboBox[SymbolPinHandleId]


class PropertiesDelegate(QStyledItemDelegate):
    def createEditor(
        self   : Self,
        parent : QWidget,
        option : QStyleOptionViewItem,
        index  : QModelIndex
    ) -> QWidget | None:
        model : QStandardItemModel = index.model()
        item : PropertiesItem = model.itemFromIndex(index)
        kind = item.kind()
        value = item.value()
        default = item.default()
        match kind:
            case "str"               : e = TextLineEditor(value, parent)
            case "float"             : e = FloatEditor(value, parent)
            case "bool"              : e = BoolEditor(value, default, parent)
            case "Text"              : e = TextEditor(value, parent)
            case "Display"           : e = EnumComboBox[PropertyDisplay](value, parent)
            case "Color"             : e = ColorComboBox(value, default, parent)
            case "LineWidth"         : e = LineWidthComboBox(value, default, parent)
            case "PenStyle"          : e = LineStyleComboBox(value, default, parent)
            case "BrushStyle"        : e = FillStyleComboBox(value, default, parent)
            case "FontFamily"        : e = FontFamilyComboBox(value, default, parent)
            case "FontSize"          : e = FontSizeComboBox(value, default, parent)
            case "FontBool"          : e = FontBoolComboBox(value, default, parent)
            case "Edge"              : e = EnumComboBox[Edge](value, parent)
            case "Direction"         : e = EnumComboBox[Direction](value, parent)
            case "RectHandleId"      : e = EnumComboBox[RectHandleId](value, parent)
            case "LineHandleId"      : e = EnumComboBox[LineHandleId](value, parent)
            case "BlockPinHandleId"  : e = EnumComboBox[BlockPinHandleId](value, parent)
            case "SymbolPinHandleId" : e = EnumComboBox[SymbolPinHandleId](value, parent)
            case _:
                logger().error(f"Invalid kind: {kind}")
                return super().createEditor(parent, option, index)
        return e

    def setEditorData(self : Self, editor : EditorType, index : QModelIndex) -> None:
        item : PropertiesItem = index.model().item(index.row(), index.column())
        editor.setValue(item.initial())

    def setModelData(
        self   : Self,
        editor : EditorType,
        model  : QStandardItemModel,
        index  : QModelIndex
    ) -> None:
        item: PropertiesItem = model.itemFromIndex(index)
        item.setValue(editor.value())
