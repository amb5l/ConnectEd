__all__ = ["PropertiesDialog", "PropertyValuesDialog", "PropertyNamesDialog"]

from typing import Self
from enum   import Enum

from PyQt6.QtCore    import Qt, QModelIndex
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, \
                            QComboBox, QPushButton, QStyledItemDelegate
from PyQt6.QtGui     import QStandardItemModel, QStandardItem, QBrush, QColor

from .table_view import TableView

from ... import hub
from ...core import logger

from ..drawing.items import ElementMixin, NO_CHANGE

from . import okCancelLayout


class PropertyChange(Enum):
    NONE     = "NONE"
    EXISTING = "EXISTING"
    ALL      = "ALL"
    DELETE   = "DELETE"

    @classmethod
    def fromStr(cls, edit : str) -> Self:
        """Convert string to PropertyEdit."""
        if edit in (
            cls.EXISTING.value,
            cls.ALL.value,
            cls.DELETE.value
        ):
            return cls(edit)
        else:
            return cls.NONE

class PropertyCell(QStandardItem):
    def __init__(self : Self, value : str | PropertyChange) -> None:
        text = value.value if isinstance(value, PropertyChange) else value
        super().__init__(text)

class PropertiesDialog(QDialog):
    model            : QStandardItemModel
    dialog_layout    : QVBoxLayout
    table_view       : TableView
    ok_cancel_layout : QHBoxLayout
    ok_button        : QPushButton
    cancel_button    : QPushButton

    def __init__(self : Self, element : ElementMixin) -> None:
        super().__init__(hub.main_window)
        self.setWindowTitle("Properties")
        self.setModal(True)
        self.dialog_layout = QVBoxLayout(self)

        # Build model
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Name", "Value"])
        if hub.settings.get("display/theme") == "dark":
            fg_fade = 0xC0C0C0; bg_fade = 0x404040
        else:
            fg_fade = 0x404040; bg_fade = 0xC0C0C0
        for name, value in element.properties.items():
            name_cell  = PropertyCell(name)
            value_cell = PropertyCell(value)
            row = [name_cell, value_cell]
            self.model.appendRow(row)

        # Set up table view
        self.table_view = TableView(self.model)
        self.table_view.setItemDelegateForColumn(3, PropertyValueEditDelegate())
        self.table_view.resizeColumnsToContents()
        self.dialog_layout.addWidget(self.table_view)

        # finish up
        okCancelLayout(self)
        self.setLayout(self.dialog_layout)
        self.adjustSize()
        min_width = self.table_view.horizontalHeader().length() + 50
        min_height = self.table_view.verticalHeader().length() + 50
        self.setMinimumSize(min_width, min_height)

    def getChoices(self : Self) -> dict[str, str]:
        """Return a dictionary of property name to value."""
        choices = {}
        for row in range(self.model.rowCount()):
            name = self.model.item(row, 0).text()
            if not name:
                logger.warning("Empty property name")
                continue
            if name in choices:
                logger.warning(f"Duplicate property name: {name}")
                continue
            value = self.model.item(row, 1).text()
            choices[name] = value
        return choices

class PropertyEditDelegate(QStyledItemDelegate):
    TOOLTIP = None

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.addItems([e.value for e in PropertyChange])
        editor.setToolTip(self.TOOLTIP)
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.ItemDataRole.EditRole)
        editor.setCurrentText(value)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentText(), Qt.ItemDataRole.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

class PropertyValueEditDelegate(PropertyEditDelegate):
    TOOLTIP = \
        "NONE: Leave property value unchanged\n" \
        "UPDATE EXISTING: Update value in elements where property exists\n" \
        "UPDATE ALL: Set value in all elements, creating property if needed\n" \
        "DELETE: Remove property from elements where it exists" \

class PropertyNameEditDelegate(PropertyEditDelegate):
    TOOLTIP = \
        "NO CHANGE: Leave property name unchanged\n" \
        "DELETE: Remove property from elements where it exists\n" \
        "UPDATE EXISTING: Update name in elements where property exists\n" \
        "UPDATE ALL: Set name in all elements, creating empty property if needed"

class PropertyValuesDialog(QDialog):
    model            : QStandardItemModel
    dialog_layout    : QVBoxLayout
    table_view       : TableView
    ok_cancel_layout : QHBoxLayout
    ok_button        : QPushButton
    cancel_button    : QPushButton

    def __init__(
        self     : Self,
        elements : list["ElementMixin"]
    ) -> None:
        super().__init__(hub.main_window)
        title = "Property Values"
        if len(elements) > 1:
            title += f" ({len(elements)} elements)"
        self.setWindowTitle(title)
        self.setModal(True)
        self.dialog_layout = QVBoxLayout(self)

        # Build dictionaries across all elements
        values = {}  # property value, <various>, or None
        nonex = {}   # non-existence count
        for element in elements:
            for name, value in element.properties.items():
                if name not in values:
                    values[name] = value
                elif values[name] is not NO_CHANGE and values[name] != value:
                    values[name] = NO_CHANGE
            for name in values.keys():
                if name not in nonex:
                    nonex[name] = 0
                if name not in element.properties.keys():
                    nonex[name] += 1

        # Build model
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(
            ["Name", "Value (Old)", "Value (New)", "Change"]
        )
        if hub.settings.get("display/theme") == "dark":
            fg_fade = 0xC0C0C0; bg_fade = 0x404040
        else:
            fg_fade = 0x404040; bg_fade = 0xC0C0C0
        for name, value in values.items():
            # name is read only
            name_cell  = PropertyCell(name)
            name_cell.setEditable(False)
            name_cell.setForeground(QColor(fg_fade))
            font = name_cell.font()
            font.setItalic(True)
            name_cell.setFont(font)
            # value (old) is read only
            value = "<various>" if value is NO_CHANGE else value
            value_old_cell = PropertyCell(value)
            value_old_cell.setEditable(False)
            value_old_cell.setForeground(QColor(fg_fade))
            font = value_old_cell.font()
            font.setItalic(True)
            value_old_cell.setFont(font)
            # value (new) is editable
            value_new_cell = PropertyCell("")
            # edit is editable via delegate
            edit_cell  = PropertyCell(PropertyChange.NONE)
            # shade name and value (old) if not all elements have the property
            if nonex[name] > 0:
                brush = QBrush(bg_fade, Qt.BrushStyle.FDiagPattern)
                name_cell.setBackground(brush)
                value_old_cell.setBackground(brush)
            row = [name_cell, value_old_cell, value_new_cell, edit_cell]
            self.model.appendRow(row)
        self.model.dataChanged.connect(self._onDataChanged)

        # Set up table view
        self.table_view = TableView(self.model)
        self.table_view.setItemDelegateForColumn(3, PropertyValueEditDelegate())
        self.table_view.resizeColumnsToContents()
        self.dialog_layout.addWidget(self.table_view)

        # finish up
        okCancelLayout(self)
        self.setLayout(self.dialog_layout)
        self.adjustSize()
        min_width = self.table_view.horizontalHeader().length() + 50
        min_height = self.table_view.verticalHeader().length() + 50
        self.setMinimumSize(min_width, min_height)

    def _onDataChanged(
        self         : Self,
        top_left     : QModelIndex,
        bottom_right : QModelIndex,
        roles        : list[int]
    ) -> None:
        """Auto-update the Change column."""
        left_col   = top_left.column()
        right_col  = bottom_right.column()
        top_row    = top_left.row()
        bottom_row = bottom_right.row()
        if not (left_col <= 2 <= right_col):
            return
        if left_col <= 3 <= right_col:
            return
        for row in range(top_row, bottom_row + 1):
            value_item = self.model.item(row, 2)
            change_item = self.model.item(row, 3)
            if value_item and change_item:
                value_text = value_item.text()
                change_text = change_item.text()
                if value_text and change_text == PropertyChange.NONE.value:
                    change_item.setText(PropertyChange.EXISTING.value)

    def getChoices(self : Self) -> dict[str, tuple[str, PropertyChange]]:
        """Return a dictionary of property name to (value, edit) tuples."""
        choices = {}
        for row in range(self.model.rowCount()):
            name = self.model.item(row, 0).text()
            if not name:
                logger.warning("Empty property name")
                continue
            if name in choices:
                logger.warning(f"Duplicate property name: {name}")
                continue
            value = self.model.item(row, 2).text()
            edit_text = self.model.item(row, 3).text()
            if edit_text not in [e.value for e in PropertyChange]:
                logger.warning(f"Invalid edit text: {edit_text}")
                continue
            edit = PropertyChange.fromStr(edit_text)
            choices[name] = (value, edit)
        return choices

class PropertyNamesDialog(QDialog):
    pass
