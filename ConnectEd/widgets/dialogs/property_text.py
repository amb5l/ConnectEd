from typing import Self

from PyQt6.QtWidgets import QWidget, QDialog, \
                            QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtGui     import QShowEvent

from ..graphics.items import QuillPref, QuillPrefChange

from ..graphics.items.property_text import PropertyTextMixin, PropertyTextBlock

from .components.line_edit              import LineEdit
from .components.text_edit              import TextEdit
from .components.layout.text_appearance import TextAppearanceLayout
from .components.layout.ok_cancel       import okCancelLayout


class PropertyTextDialog(QDialog):
    _dialog_layout     : QVBoxLayout
    _value_layout      : QHBoxLayout
    _value_label       : QLabel
    _value_edit        : LineEdit | TextEdit
    _appearance_layout : TextAppearanceLayout
    _ok_cancel_layout  : QHBoxLayout
    _ok_button         : QPushButton
    _cancel_button     : QPushButton

    def __init__(
        self   : Self,
        item   : PropertyTextMixin,
        parent : QWidget | None = None # not to be confused with _parent
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"Property Text: {item.name()}")
        self.setModal(True)
        self._dialog_layout = QVBoxLayout(self)
        if isinstance(item, PropertyTextBlock):
            self._value_layout = QVBoxLayout()
            self._value_edit = TextEdit(item.value())
        else:
            self._value_layout = QHBoxLayout()
            self._value_edit = LineEdit(item.value())
        self._value_label = QLabel("Value:")
        self._value_layout.addWidget(self._value_label)
        self._value_layout.addWidget(self._value_edit)
        self._dialog_layout.addLayout(self._value_layout)
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

    def getAppearanceChange(self : Self) -> QuillPrefChange:
        return self._appearance_layout.getChoice()
