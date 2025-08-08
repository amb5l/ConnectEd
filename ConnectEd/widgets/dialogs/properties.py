from typing import Self, Any
from dataclasses import dataclass

from PyQt6.QtCore    import Qt, QModelIndex
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, \
                            QComboBox, QPushButton, QStyledItemDelegate, \
                            QLineEdit
from PyQt6.QtGui     import QStandardItemModel, QStandardItem, QBrush

from .table_view import TableView

from ... import hub

from ...core.log   import logger
from ...core.utils import str2val

from ..drawing.properties import PropertiesMixin

from ..drawing.items import Edge
from ..drawing.items.property_text import PropertyDisplay


class PropertiesItem(QStandardItem):
    IDX_TYPE_NAME    = 0
    IDX_INITIAL_TEXT = 1

    def __init__(self : Self, text : str) -> None:
        super().__init__(text)
        self.setInitialText(text)

    def setInitialText(self : Self, text : str) -> None:
        self.setData(text, Qt.ItemDataRole.UserRole + self.IDX_INITIAL_TEXT)

    def getInitialText(self : Self) -> str:
        return self.data(Qt.ItemDataRole.UserRole + self.IDX_INITIAL_TEXT)

    def changed(self : Self) -> bool:
        return self.text() != self.getInitialText()

class NameItem(PropertiesItem):
    def __init__(self : Self, name : str, custom : bool = False) -> None:
        super().__init__(name)
        self.setEditable(custom)

class ValueItem(PropertiesItem):
    def __init__(
        self      : Self,
        value     : Any,
        type_name : str,
        read_only : bool = False
    ) -> None:
        super().__init__(str(value))
        self.setTypeName(type_name)
        self.setInitialText(str(value))
        self.setEditable(not read_only)

    def setTypeName(self : Self, type_name : str) -> None:
        self.setData(type_name, Qt.ItemDataRole.UserRole + self.IDX_TYPE_NAME)

    def getTypeName(self : Self) -> str:
        return self.data(Qt.ItemDataRole.UserRole + self.IDX_TYPE_NAME)

class DescriptionItem(PropertiesItem):
    def __init__(self : Self, description : str, custom : bool = False) -> None:
        super().__init__(description)
        self.setEditable(custom)

class ValueDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        value_type = index.model().data(index, Qt.ItemDataRole.UserRole)
        match value_type:
            case "str" | "float":
                editor = QLineEdit(parent)
                editor.setPlaceholderText("Enter text")
            case "Edge":
                editor = QComboBox(parent)
                editor.addItems([e.value for e in Edge])
            case _:
                editor = None
                logger.error(f"Invalid value type: {value_type}")
        return super().createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.ItemDataRole.EditRole)
        if isinstance(editor, QLineEdit):
            editor.setText(str(value) if value else "")
        elif isinstance(editor, QComboBox):
            editor.setCurrentText(str(value) if value else "")
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        if isinstance(editor, QLineEdit):
            model.setData(index, editor.text(), Qt.ItemDataRole.EditRole)
        elif isinstance(editor, QComboBox):
            model.setData(index, editor.currentText(), Qt.ItemDataRole.EditRole)
        else:
            super().setModelData(editor, model, index)

@dataclass
class PropertyState:
    name        : str
    value       : Any
    description : str

class PropertiesDialog(QDialog):
    _dialog_layout  : QVBoxLayout
    _table_model    : QStandardItemModel
    _table_view     : TableView
    _value_delegate : ValueDelegate
    _button_layout  : QHBoxLayout
    _new_button     : QPushButton
    _ok_button      : QPushButton
    _cancel_button  : QPushButton

    def __init__(self: Self, element: PropertiesMixin) -> None:
        # initialise
        super().__init__(hub.main_window)
        self.setWindowTitle("Properties")
        self.setModal(True)
        self._dialog_layout = QVBoxLayout(self)
        # build model
        self._table_model = QStandardItemModel()
        self._table_model.setHorizontalHeaderLabels([
            "Name",
            "Value",
            "Description"
        ])
        for name, spec in element._PROPERTY_SPECS.items():
            custom = spec.custom
            value = spec.getter(element)
            value_type = spec.type_name
            read_only = spec.setter is None
            description = spec.description
            self._table_model.appendRow([
                NameItem(name, custom),
                ValueItem(value, value_type, read_only),
                DescriptionItem(description, custom)
            ])
        # create delegate
        self._value_delegate = ValueDelegate()
        self._value_delegate.destroyed.connect(
            lambda: self.onDelegateDestroyed("Value")
        )
        # build table view
        self._table_view = TableView(self._table_model)
        self._table_view.setItemDelegateForColumn(0, self._value_delegate)
        self._table_view.resizeColumnsToContents()
        # build button layout
        self._button_layout = QHBoxLayout()
        self._new_button = QPushButton("New")
        self._new_button.clicked.connect(self.new)
        self._button_layout.addWidget(self._new_button)
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

    def onDelegateDestroyed(self, delegate_name: str) -> None:
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

    def new(self: Self) -> None:
        row = self._table_model.rowCount()
        self._table_model.appendRow([
            NameItem("", True),
            ValueItem("", "str"),
            "user defined property"
        ])
        self._table_view.setCurrentIndex(self._table_model.index(row, 0))

    def getChanges(self: Self) -> dict[str, PropertyState]:
        r = {}
        for row_num in range(self._table_model.rowCount()):
            name_item : NameItem = self._table_model.item(row_num, 0)
            value_item : ValueItem = self._table_model.item(row_num, 1)
            description_item : DescriptionItem = self._table_model.item(row_num, 2)
            name_changed = name_item.changed()
            value_changed = value_item.changed()
            description_changed = description_item.changed()
            if name_changed or value_changed or description_changed:
                old_name = name_item.getInitialText()
                new_name = name_item.text()
                new_value = str2val(value_item.text(), value_item.getTypeName())
                new_description = description_item.text()
                change = PropertyState(
                    new_name,
                    new_value,
                    new_description
                )
                r[old_name] = change
        return r
