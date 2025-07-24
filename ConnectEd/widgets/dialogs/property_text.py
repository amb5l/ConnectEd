__all__ = ["PropertyTextDialog"]

from typing import Self

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,\
                            QLabel, QComboBox, QLineEdit, QPushButton
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from ...core import logger

from ..drawing.items import PropertyText, QuillPref, QuillPrefChange

from .appearance import TextAppearanceLayout

from . import okCancelLayout

from ... import hub


class PropertyTextDialog(QDialog):
    dialog_layout     : QVBoxLayout
    name_value_layout : QHBoxLayout
    name_label        : QLabel
    name_edit         : QComboBox
    value_layout      : QHBoxLayout
    value_label       : QLabel
    value_edit        : QLineEdit
    appearance_layout : TextAppearanceLayout
    ok_cancel_layout  : QHBoxLayout
    ok_button         : QPushButton
    cancel_button     : QPushButton

    def __init__(self : Self, element : PropertyText):
        super().__init__(hub.main_window)
        self.setWindowTitle("Property Text")
        self.setModal(True)
        self.element = element
        self.parent = element.parentItem()
        if self.parent is None:
            self.parent = element.scene()
        if self.parent is None:
            logger.warning("Parent item not found")
        self.dialog_layout = QVBoxLayout(self)
        self.name_value_layout = QGridLayout()
        self.name_label = QLabel("Name:")
        self.name_value_layout.addWidget(self.name_label, 0, 0)
        self.name_edit = QComboBox()
        self.name_edit.addItems(self.parent.getProperties())
        self.name_edit.setCurrentText(element.name())
        self.name_edit.currentTextChanged.connect(self.onPropertyNameChanged)
        self.name_value_layout.addWidget(self.name_edit, 0, 1)
        self.value_label = QLabel("Value:")
        self.name_value_layout.addWidget(self.value_label, 1, 0)
        self.value_edit = QLineEdit(element.value())
        self.name_value_layout.addWidget(self.value_edit, 1, 1)
        self.dialog_layout.addLayout(self.name_value_layout)

        initial = element.quill.getPref()
        defaults = element.quill.getDefaults()
        default = QuillPref(
            color     = defaults.color,
            family    = defaults.family,
            size      = defaults.size,
            bold      = defaults.bold,
            italic    = defaults.italic,
            underline = defaults.underline
        )
        self.appearance_layout = TextAppearanceLayout(initial, default)
        self.dialog_layout.addLayout(self.appearance_layout)

        okCancelLayout(self)
        self.setLayout(self.dialog_layout)

    def onPropertyNameChanged(self, name: str) -> None:
        self.value_edit.setText(self.parent.getProperty(name))

    def showEvent(self, event):
        """Override showEvent to select value text when dialog appears."""
        super().showEvent(event)
        self.value_edit.selectAll()
        self.value_edit.setFocus()

    def getName(self : Self) -> str:
        return self.name_edit.currentText()

    def getValue(self : Self) -> str:
        return self.value_edit.text()

    def getAppearanceChange(self : Self) -> QuillPrefChange:
        return self.appearance_layout.getChoice()
