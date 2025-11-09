from typing import Self

from PyQt6.QtCore    import Qt, QModelIndex
from PyQt6.QtWidgets import QWidget, QStyledItemDelegate, QStyleOptionViewItem
from PyQt6.QtGui     import QStandardItem, QStandardItemModel

from ....app import logger

from ....core.utils import str2val, val2str

from .line_edit        import StringEdit, IntEdit, FloatEdit
from .combo.color      import ColorComboBox
from .combo.line_width import LineWidthComboBox
from .combo.line_style import LineStyleComboBox
from .combo.fill_style import FillStyleComboBox
from .combo.font_size  import FontSizeComboBox
from .combo.on_off     import OnOffComboBox
from .combo.edge       import EdgeComboBox


class ValueDelegate(QStyledItemDelegate):
    def createEditor(
        self   : Self,
        parent : QWidget,
        option : QStyleOptionViewItem,
        index  : QModelIndex
    ) -> QWidget | None:
        item : QStandardItem = index.model().item(index.row(), index.column())
        item_type = item.getTypeName()
        item_value = str2val(item.text(), item_type)
        name_index = index.model().index(index.row(), 0)
        name_text = index.model().data(name_index, Qt.ItemDataRole.DisplayRole)
        if item_type == "float":
            if name_text == "Line Width":
                item_type = "LineWidth"
            elif name_text == "Text Size":
                item_type = "FontSize"
        if hasattr(item, "getDefault"):
            default = item.getDefault()
        match item_type:
            case "str":
                editor = StringEdit(item_value, parent)
            case "int":
                editor = IntEdit(item_value, parent)
            case "float":
                editor = FloatEdit(item_value, parent)
            case "Edge":
                editor = EdgeComboBox(item_value, parent)
            case "QColor":
                editor = ColorComboBox(item_value, default, None, parent)
            case "LineWidth":
                editor = LineWidthComboBox(item_value, default, None, parent)
            case "PenStyle":
                editor = LineStyleComboBox(item_value, default, None, parent)
            case "BrushStyle":
                editor = FillStyleComboBox(item_value, default, None, parent)
            case "FontSize":
                editor = FontSizeComboBox(item_value, default, None, parent)
            case "bool":
                editor = OnOffComboBox(item_value, default, None, parent)
            case _:
                editor = None
                logger().error(f"Invalid value type: {item_type}")
                return super().createEditor(parent, option, index)
        return editor

    def setEditorData(self : Self, editor : QWidget, index : QModelIndex) -> None:
        item : QStandardItem = index.model().item(index.row(), index.column())
        text = item.text()
        if isinstance(editor, StringEdit):
            editor.setText(text)
        elif isinstance(editor, IntEdit | FloatEdit):
            value = str2val(text, item.getTypeName())
            editor.setValue(value)
        elif isinstance(editor, EdgeComboBox | \
            ColorComboBox | LineWidthComboBox | LineStyleComboBox | \
            FillStyleComboBox | FontSizeComboBox | OnOffComboBox
        ):
            pass
        else:
            super().setEditorData(editor, index)

    def setModelData(
        self   : Self,
        editor : QWidget,
        model  : QStandardItemModel,
        index  : QModelIndex
    ) -> None:
        if isinstance(editor, StringEdit):
            text = editor.text()
        elif isinstance(editor, FloatEdit | IntEdit):
            text = val2str(editor.getValue())
        elif isinstance(editor, EdgeComboBox |\
            ColorComboBox | LineWidthComboBox | LineStyleComboBox | \
            FillStyleComboBox | FontSizeComboBox | OnOffComboBox
        ):
            text = val2str(editor.getChoice())
        else:
            super().setModelData(editor, model, index)
            return
        model.setData(index, text, Qt.ItemDataRole.DisplayRole)
