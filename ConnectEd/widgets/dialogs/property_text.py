from typing import Self

from PyQt6.QtWidgets import QWidget, QDialog, \
                            QVBoxLayout, QHBoxLayout, QGridLayout,\
                            QLabel, QComboBox, QLineEdit, QPushButton
from PyQt6.QtGui     import QShowEvent

from ..graphics.items import QuillPref, QuillPrefChange

from ..graphics.items.property_text import PropertyText, PropertyDisplay

from .components.layout.text_appearance import TextAppearanceLayout

from .components.layout.ok_cancel import okCancelLayout


class PropertyTextDialog(QDialog):
    _dialog_layout     : QVBoxLayout
    _vd_layout         : QGridLayout  # value, display
    _value_label       : QLabel
    _value_edit        : QLineEdit
    _display_label     : QLabel
    _display_combo     : QComboBox
    _appearance_layout : TextAppearanceLayout
    _ok_cancel_layout  : QHBoxLayout
    _ok_button         : QPushButton
    _cancel_button     : QPushButton

    def __init__(
        self   : Self,
        item   : PropertyText,
        parent : QWidget | None = None # not to be confused with _parent
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"Property Text: {item.name()}")
        self.setModal(True)
        self._dialog_layout = QVBoxLayout(self)
        self._vd_layout = QGridLayout()
        self._value_label = QLabel("Value:")
        self._vd_layout.addWidget(self._value_label, 0, 0)
        self._value_edit = QLineEdit(item.value())
        self._vd_layout.addWidget(self._value_edit, 0, 1)
        self._display_label = QLabel("Display:")
        self._vd_layout.addWidget(self._display_label, 1, 0)
        self._display_combo = QComboBox()
        self._display_combo.addItems(ad.value for ad in PropertyDisplay)
        self._display_combo.setCurrentText(str(item.display()))
        self._vd_layout.addWidget(self._display_combo, 1, 1)
        self._dialog_layout.addLayout(self._vd_layout)

        initial = item.a.quill.getPref()
        defaults = item.a.quill.getDefaults()
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

    def showEvent(self : Self, event : QShowEvent):
        """Override showEvent to select value text when dialog appears."""
        super().showEvent(event)
        self._value_edit.selectAll()
        self._value_edit.setFocus()

    def getValue(self : Self) -> str:
        return self._value_edit.text()

    def getDisplay(self : Self) -> PropertyDisplay:
        return PropertyDisplay(self._display_combo.currentText())

    def getAppearanceChange(self : Self) -> QuillPrefChange:
        return self._appearance_layout.getChoice()
