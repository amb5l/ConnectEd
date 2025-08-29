from typing import Self

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, \
                            QLabel, QTextEdit, QPushButton

from ... import hub

from ..graphics.items import ElementQuillMixin, QuillPref, QuillPrefChange

from .appearance import TextAppearanceLayout

from . import okCancelLayout


class TextBlockDialog(QDialog):
    _dialog_layout     : QVBoxLayout
    _text_layout       : QVBoxLayout
    _text_label        : QLabel
    _text_edit         : QTextEdit
    _appearance_layout : TextAppearanceLayout
    _ok_cancel_layout  : QHBoxLayout
    _ok_button         : QPushButton
    _cancel_button     : QPushButton

    def __init__(
        self    : Self,
        element : ElementQuillMixin
    ):
        super().__init__(hub.main_window)
        self.setWindowTitle("Text Block")
        self.setModal(True)
        self._dialog_layout = QVBoxLayout(self)

        self._text_layout = QVBoxLayout()
        self._text_label = QLabel("Text:")
        self._text_layout.addWidget(self._text_label)
        self._text_edit = QTextEdit(element.toPlainText())
        self._text_edit.setMinimumSize(400, 200)  # Give more space for multi-line text
        self._text_layout.addWidget(self._text_edit)
        self._dialog_layout.addLayout(self._text_layout)

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

    def showEvent(self, event):
        """Override showEvent to select all text when dialog appears."""
        super().showEvent(event)
        if self._text_edit.toPlainText() == "<text>":
            self._text_edit.selectAll()
            self._text_edit.setFocus()

    def getChoice(self : Self) -> tuple[str, QuillPrefChange]:
        text = self._text_edit.toPlainText()
        appearance = self._appearance_layout.getChoice()
        return text, appearance
