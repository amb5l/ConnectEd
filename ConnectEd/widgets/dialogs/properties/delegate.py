from typing import Self

from PyQt6.QtCore    import QModelIndex
from PyQt6.QtWidgets import QWidget, QStyledItemDelegate, QStyleOptionViewItem
from PyQt6.QtGui     import QStandardItemModel

from ....app import logger

from ..components.edit import (
    TextLineEditor,
    FloatEditor,
    BoolEditor,
    TextEditor
)

from ..components.combo.display     import DisplayComboBox
from ..components.combo.color       import ColorComboBox
from ..components.combo.line_width  import LineWidthComboBox
from ..components.combo.line_style  import LineStyleComboBox
from ..components.combo.fill_style  import FillStyleComboBox
from ..components.combo.font_family import FontFamilyComboBox
from ..components.combo.font_size   import FontSizeComboBox
from ..components.combo.font_bool   import FontBoolComboBox
from ..components.combo.edge        import EdgeComboBox
from ..components.combo.direction   import DirectionComboBox


from .item import PropertiesItem


class Delegate(QStyledItemDelegate):
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
            case "str"               : editor = TextLineEditor(value, parent)
            case "float"             : editor = FloatEditor(value, parent)
            case "bool"              : editor = BoolEditor(value, default, parent)
            case "Text"              : editor = TextEditor(value, parent)
            case "Display"           : editor = DisplayComboBox(value, parent)
            case "Color"             : editor = ColorComboBox(value, default, parent)
            case "LineWidth"         : editor = LineWidthComboBox(value, default, parent)
            case "PenStyle"          : editor = LineStyleComboBox(value, default, parent)
            case "BrushStyle"        : editor = FillStyleComboBox(value, default, parent)
            case "FontFamily"        : editor = FontFamilyComboBox(value, default, parent)
            case "FontSize"          : editor = FontSizeComboBox(value, default, parent)
            case "FontBool"          : editor = FontBoolComboBox(value, default, parent)
            case "Edge"              : editor = EdgeComboBox(value, parent)
            case "Direction"         : editor = DirectionComboBox(value, parent)
            case "RectHandleId"      : editor = RectHandleIdComboBox(value, parent)
            case "LineHandleId"      : editor = LineHandleIdComboBox(value, parent)
            case "BlockPinHandleId"  : editor = BlockPinHandleIdComboBox(value, parent)
            case "SymbolPinHandleId" : editor = SymbolPinHandleIdComboBox(value, parent)
            case _:
                editor = None
                logger().error(f"Invalid kind: {kind}")
                return super().createEditor(parent, option, index)
        return editor

    def setEditorData(self : Self, editor : QWidget, index : QModelIndex) -> None:
        item : PropertiesItem = index.model().item(index.row(), index.column())
        editor.setValue(item.initial())

    def setModelData(
        self   : Self,
        editor : QWidget,
        model  : QStandardItemModel,
        index  : QModelIndex
    ) -> None:

        item: PropertiesItem = model.itemFromIndex(index)
        value = editor.value()



        if isinstance(editor, TextLineEditor):
            text = editor.text()
        elif isinstance(editor, FloatEditor | IntEditor):
            text = val2str(editor.value())
        elif isinstance(editor, EdgeComboBox | DisplayComboBox |\
            ColorComboBox | LineWidthComboBox | LineStyleComboBox | \
            FillStyleComboBox | FontSizeComboBox | FontBool
        ):
            text = val2str(editor.getChoice())
        else:
            super().setModelData(editor, model, index)
            return
        # Validate names (column 0) to prevent duplicates
        if index.column() == 0 and text:  # name column and not empty
            existing_names = [
                model.item(row, 0).text() \
                for row in range(model.rowCount()) if row != index.row()
            ]
            if text in existing_names:
                QMessageBox.warning(
                    editor.parent(),
                    "Duplicate Name",
                    f"The property name '{text}' already exists."
                )
                model.setData(index, "", Qt.ItemDataRole.DisplayRole)
                return
        model.setData(index, text, Qt.ItemDataRole.DisplayRole)