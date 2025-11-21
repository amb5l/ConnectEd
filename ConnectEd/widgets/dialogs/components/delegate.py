from typing import Self

from PyQt6.QtCore    import Qt, QModelIndex
from PyQt6.QtWidgets import QWidget, QStyledItemDelegate, QStyleOptionViewItem, \
                            QMessageBox
from PyQt6.QtGui     import QStandardItem, QStandardItemModel

from ....app import logger

from ....core.utils import str2val, val2str

from .model                 import DialogItem
from .line_edit             import StringEdit, IntEdit, FloatEdit
from .combo.color           import ColorComboBox
from .combo.display_choice  import DisplayChoiceComboBox
from .combo.line_width      import LineWidthComboBox
from .combo.line_style      import LineStyleComboBox
from .combo.fill_style      import FillStyleComboBox
from .combo.font_family     import FontFamilyComboBox
from .combo.font_size       import FontSizeComboBox
from .combo.on_off          import OnOffComboBox
from .combo.edge            import EdgeComboBox


class DialogItemDelegate(QStyledItemDelegate):
    def createEditor(
        self   : Self,
        parent : QWidget,
        option : QStyleOptionViewItem,
        index  : QModelIndex
    ) -> QWidget | None:
        item : DialogItem = index.model().item(index.row(), index.column())
        item_type = item.getKind()
        item_value = item.getValue()
        item_default = item.getDefault()
        match item_type:
            case "str":
                editor = StringEdit(item_value, parent)
            case "int":
                editor = IntEdit(item_value, parent)
            case "float":
                editor = FloatEdit(item_value, parent)
            case "bool":
                editor = OnOffComboBox(item_value, item_default, None, parent)
            case "Edge":
                editor = EdgeComboBox(item_value, parent)
            case "QColor":
                editor = ColorComboBox(item_value, item_default, None, parent)
            case "DisplayChoice":
                editor = DisplayChoiceComboBox(item_value, parent)
            case "FontFamily":
                editor = FontFamilyComboBox(item_value, item_default, None, parent)
            case "LineWidth":
                editor = LineWidthComboBox(item_value, item_default, None, parent)
            case "PenStyle":
                editor = LineStyleComboBox(item_value, item_default, None, parent)
            case "BrushStyle":
                editor = FillStyleComboBox(item_value, item_default, None, parent)
            case "FontSize":
                editor = FontSizeComboBox(item_value, item_default, None, parent)
            case _:
                editor = None
                logger().error(f"Invalid value type: {item_type}")
                return super().createEditor(parent, option, index)
        return editor

    def setEditorData(self : Self, editor : QWidget, index : QModelIndex) -> None:
        item : DialogItem = index.model().item(index.row(), index.column())
        text = item.text()
        if isinstance(editor, StringEdit):
            editor.setText(text)
        elif isinstance(editor, IntEdit | FloatEdit):
            value = str2val(text, item.getKind())
            editor.setValue(value)
        elif isinstance(editor, EdgeComboBox | DisplayChoiceComboBox | \
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
        elif isinstance(editor, EdgeComboBox | DisplayChoiceComboBox |\
            ColorComboBox | LineWidthComboBox | LineStyleComboBox | \
            FillStyleComboBox | FontSizeComboBox | OnOffComboBox
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
