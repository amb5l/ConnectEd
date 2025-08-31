from typing import Self, Any, Optional
from dataclasses import dataclass

from PyQt6.QtCore    import Qt, QModelIndex
from PyQt6.QtWidgets import QWidget, QDialog, QVBoxLayout, QHBoxLayout, \
                            QPushButton, QStyledItemDelegate, QAbstractItemView
from PyQt6.QtGui     import QStandardItemModel, QStandardItem, QBrush

from .table_view import TableView

from ... import hub

from ...core.log   import logger
from ...core.utils import str2val, val2str

from ..graphics.properties import PropertiesMixin

from ..graphics.items import DEFAULT

from .components import ColorComboBox,      \
                        LineWidthComboBox,  \
                        LineStyleComboBox,  \
                        FillStyleComboBox,  \
                        FontFamilyComboBox, \
                        FontSizeComboBox,   \
                        OnOffComboBox,      \
                        StringEdit,         \
                        IntEdit,            \
                        FloatEdit,          \
                        EdgeComboBox


@dataclass
class PropertyState:
    name        : str
    value       : Any
    description : str

@dataclass
class PropertyChange:
    before : Optional[PropertyState]
    after  : Optional[PropertyState]

class PropertiesItem(QStandardItem):
    IDX_INITIAL_TEXT = 0

    def __init__(self : Self, text : str) -> None:
        super().__init__(text)
        self.setInitialText(text)

    def setInitialText(self : Self, text : str) -> None:
        self.setData(text, Qt.ItemDataRole.UserRole + self.IDX_INITIAL_TEXT)

    def getInitialText(self : Self) -> str:
        return self.data(Qt.ItemDataRole.UserRole + self.IDX_INITIAL_TEXT)

    def changed(self : Self) -> bool:
        current_text = self.text()
        return current_text != self.getInitialText()

class NameItem(PropertiesItem):
    def __init__(self : Self, name : str, custom : bool = False) -> None:
        super().__init__(name)
        self.setEditable(custom)

class ValueItem(PropertiesItem):
    IDX_TYPE_NAME = 1
    IDX_DEFAULT = 2

    def __init__(
        self      : Self,
        type_name : str,
        value     : Any,
        default   : Any  = None,
        read_only : bool = False
    ) -> None:
        text = val2str(value)
        super().__init__(text)
        self.setTypeName(type_name)
        if default is not None:
            self.setDefault(default)
        self.setEditable(not read_only)

    def setTypeName(self : Self, type_name : str) -> None:
        self.setData(type_name, Qt.ItemDataRole.UserRole + self.IDX_TYPE_NAME)

    def getTypeName(self : Self) -> str:
        return self.data(Qt.ItemDataRole.UserRole + self.IDX_TYPE_NAME)

    def setDefault(self : Self, default : Any) -> None:
        self.setData(default, Qt.ItemDataRole.UserRole + self.IDX_DEFAULT)

    def getDefault(self : Self) -> Any:
        return self.data(Qt.ItemDataRole.UserRole + self.IDX_DEFAULT)

class DescriptionItem(PropertiesItem):
    def __init__(self : Self, description : str, custom : bool = False) -> None:
        super().__init__(description)
        self.setEditable(custom)

class ValueDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        item : ValueItem = index.model().item(index.row(), index.column())
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
                logger.error(f"Invalid value type: {item_type}")
                return super().createEditor(parent, option, index)
        return editor

    def setEditorData(self, editor, index):
        item : ValueItem = index.model().item(index.row(), index.column())
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

    def setModelData(self, editor, model, index):
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

class PropertiesDialog(QDialog):
    _dialog_layout  : QVBoxLayout
    _table_model    : QStandardItemModel
    _table_view     : TableView
    _value_delegate : ValueDelegate
    _button_layout  : QHBoxLayout
    _add_button     : QPushButton
    _delete_button  : QPushButton
    _ok_button      : QPushButton
    _cancel_button  : QPushButton
    _initial        : dict[str, tuple[Any, str]]

    def __init__(
        self    : Self,
        element : PropertiesMixin,
        parent  : Optional[QWidget] = None
    ) -> None:
        # initialise
        super().__init__(parent)
        self.setWindowTitle("Properties")
        self.setModal(True)
        self._dialog_layout = QVBoxLayout(self)
        # build model
        self._initial = {}
        self._table_model = QStandardItemModel()
        self._table_model.setHorizontalHeaderLabels([
            "Name",
            "Value",
            "Description"
        ])
        for name, spec in element._PROPERTY_SPECS.items():
            custom = spec.custom
            value = spec.getter(element)
            type_name = spec.type_name
            default = spec.default
            read_only = spec.setter is None
            description = spec.description
            self._table_model.appendRow([
                NameItem(name, custom),
                ValueItem(type_name, value, default, read_only),
                DescriptionItem(description, custom)
            ])
            self._initial[name] = (value, description)
        # create delegate
        self._value_delegate = ValueDelegate()
        self._value_delegate.destroyed.connect(
            lambda: self.onDelegateDestroyed("Value")
        )
        # build table view
        self._table_view = TableView(self._table_model)
        self._table_view.setItemDelegateForColumn(1, self._value_delegate)
        self._table_view.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked |
            QAbstractItemView.EditTrigger.EditKeyPressed |
            QAbstractItemView.EditTrigger.AnyKeyPressed
        )
        self._table_view.resizeColumnsToContents()
        self._table_view.setColumnWidth(1, self._getValueColumnWidth())
        # build button layout
        self._button_layout = QHBoxLayout()
        self._add_button = QPushButton("New")
        self._add_button.clicked.connect(self.add)
        self._button_layout.addWidget(self._add_button)
        self._delete_button = QPushButton("Delete")
        self._delete_button.clicked.connect(self.delete)
        self._button_layout.addWidget(self._delete_button)
        self._button_layout.addStretch()
        self._ok_button = QPushButton("OK")
        self._ok_button.clicked.connect(self.accept)
        self._button_layout.addWidget(self._ok_button)
        self._cancel_button = QPushButton("Cancel")
        self._cancel_button.clicked.connect(self.reject)
        self._button_layout.addWidget(self._cancel_button)
        # finalise
        self._dialog_layout.addWidget(self._table_view)
        self._dialog_layout.addLayout(self._button_layout)
        self.setLayout(self._dialog_layout)
        self.adjustSize()
        min_width = self._table_view.horizontalHeader().length() + 50
        min_height = self._table_view.verticalHeader().length() + 50
        self.setMinimumSize(min_width, min_height)
        self._table_model.dataChanged.connect(self.onDataChanged)

    def _getValueColumnWidth(self: Self) -> int:
        max_width = 50  # minimum width
        test_editors = [
            ColorComboBox     (DEFAULT, DEFAULT, DEFAULT, None),
            LineWidthComboBox (DEFAULT, DEFAULT, DEFAULT, None),
            LineStyleComboBox (DEFAULT, DEFAULT, DEFAULT, None),
            FillStyleComboBox (DEFAULT, DEFAULT, DEFAULT, None)
        ]
        for editor in test_editors:
            if editor:
                hint = editor.sizeHint()
                max_width = max(max_width, hint.width())
                editor.deleteLater()  # Clean up
        return max_width + 20  # padding

    def onDelegateDestroyed(self, _: str) -> None:
        """Workaround to fix delegate lifecycle issue (silent crash)."""
        pass

    def onDataChanged(
        self: Self,
        top_left: QModelIndex,
        bottom_right: QModelIndex,
        roles: list[int]
    ) -> None:
        if hub.settings.get("display/theme") == "dark":
            bg_highlight = Qt.GlobalColor.darkYellow
        else:
            bg_highlight = Qt.GlobalColor.yellow
        for row in range(top_left.row(), bottom_right.row() + 1):
            for col in range(top_left.column(), bottom_right.column() + 1):
                item : PropertiesItem = self._table_model.item(row, col)
                if item and item.changed():
                    item.setBackground(QBrush(bg_highlight))
                else:
                    item.setBackground(QBrush(Qt.GlobalColor.transparent))

    def add(self: Self) -> None:
        row = self._table_model.rowCount()
        self._table_model.appendRow([
            NameItem("", True),
            ValueItem("", "str"),
            DescriptionItem("user defined property", True)
        ])
        self._table_view.setCurrentIndex(self._table_model.index(row, 0))

    def delete(self: Self) -> None:
        row = self._table_view.currentIndex().row()
        name_item : NameItem = self._table_model.item(row, 0)
        if name_item.isEditable():
            self._table_model.removeRow(row)

    def getChanges(self: Self) -> list[PropertyChange]:
        r = []
        initial_names = list(self._initial.keys())
        # changed and new properties
        for row in range(self._table_model.rowCount()):
            name_item : NameItem = self._table_model.item(row, 0)
            value_item : ValueItem = self._table_model.item(row, 1)
            type_name = value_item.getTypeName()
            description_item : DescriptionItem = self._table_model.item(row, 2)
            new_name = name_item.text()
            new_value = str2val(value_item.text(), type_name)
            new_description = description_item.text()
            new_state = PropertyState(new_name, new_value, new_description)
            old_name = name_item.getInitialText()
            if old_name == "":
                old_state = None # new property
            else:
                initial_names.remove(old_name)
                old_value = str2val(value_item.getInitialText(), type_name)
                old_description = description_item.getInitialText()
                old_state = PropertyState(old_name, old_value, old_description)
            r.append(PropertyChange(old_state, new_state))
        # deleted properties
        for initial_name in initial_names:
            initial_value, initial_description = self._initial[initial_name]
            initial_state = PropertyState(
                initial_name, initial_value, initial_description
            )
            r.append(PropertyChange(initial_state, None))
        return r
