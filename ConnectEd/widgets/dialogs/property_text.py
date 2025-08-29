from typing import Self

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,\
                            QLabel, QComboBox, QLineEdit, QPushButton

from ... import hub

from ...core.log import logger

from ..graphics.properties import PropertiesMixin

from ..graphics.items import QuillPref, QuillPrefChange

from ..graphics.items.anchor_point  import AnchorPoint
from ..graphics.items.property_text import PropertyText, PropertyDisplay

from .components import TextAppearanceLayout

from . import okCancelLayout


class PropertyTextDialog(QDialog):
    _parent            : PropertiesMixin
    _dialog_layout     : QVBoxLayout
    _nvd_layout        : QGridLayout  # name, value, display
    _name_label        : QLabel
    _name_edit         : QComboBox
    _value_label       : QLabel
    _value_edit        : QLineEdit
    _display_label     : QLabel
    _display_combo     : QComboBox
    _appearance_layout : TextAppearanceLayout
    _ok_cancel_layout  : QHBoxLayout
    _ok_button         : QPushButton
    _cancel_button     : QPushButton

    def __init__(self : Self, element : PropertyText):
        super().__init__(hub.main_window)
        self.setWindowTitle("Property Text")
        self.setModal(True)
        self._parent = element.parent()
        self._dialog_layout = QVBoxLayout(self)
        self._nvd_layout = QGridLayout()
        self._name_label = QLabel("Name:")
        self._nvd_layout.addWidget(self._name_label, 0, 0)
        self._name_edit = QComboBox()
        self._name_edit.addItems(self._parent.getPropertyNames())
        self._name_edit.setCurrentText(element.name())
        self._name_edit.currentTextChanged.connect(self.onPropertyNameChanged)
        self._nvd_layout.addWidget(self._name_edit, 0, 1)
        self._value_label = QLabel("Value:")
        self._nvd_layout.addWidget(self._value_label, 1, 0)
        self._value_edit = QLineEdit(element.value())
        self._nvd_layout.addWidget(self._value_edit, 1, 1)
        self._display_label = QLabel("Display:")
        self._nvd_layout.addWidget(self._display_label, 2, 0)
        self._display_combo = QComboBox()
        self._display_combo.addItems(pd.value for pd in PropertyDisplay)
        self._display_combo.setCurrentText(str(element.display()))
        self._nvd_layout.addWidget(self._display_combo, 2, 1)
        self._dialog_layout.addLayout(self._nvd_layout)

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
        self._appearance_layout = TextAppearanceLayout(initial, default)
        self._dialog_layout.addLayout(self._appearance_layout)

        okCancelLayout(self)
        self.setLayout(self._dialog_layout)

    def onPropertyNameChanged(self, name: str) -> None:
        self._value_edit.setText(self._parent.getProperty(name))

    def showEvent(self, event):
        """Override showEvent to select value text when dialog appears."""
        super().showEvent(event)
        self._value_edit.selectAll()
        self._value_edit.setFocus()

    def getName(self : Self) -> str:
        return self._name_edit.currentText()

    def getValue(self : Self) -> str:
        return self._value_edit.text()

    def getDisplay(self : Self) -> PropertyDisplay:
        return PropertyDisplay(self._display_combo.currentText())

    def getAppearanceChange(self : Self) -> QuillPrefChange:
        return self._appearance_layout.getChoice()
