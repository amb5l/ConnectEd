__all__ = ["TextDialog"]

from typing import Self

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, \
                            QLabel, QLineEdit, QPushButton

from ... import hub

from ..drawing.items import ElementQuillMixin, QuillPref, QuillPrefChange

from .appearance import TextAppearanceLayout

from . import okCancelLayout


class TextDialog(QDialog):
    dialog_layout     : QVBoxLayout
    text_layout       : QHBoxLayout
    text_label        : QLabel
    text_edit         : QLineEdit
    appearance_layout : TextAppearanceLayout
    ok_cancel_layout  : QHBoxLayout
    ok_button         : QPushButton
    cancel_button     : QPushButton

    def __init__(
        self    : Self,
        element : ElementQuillMixin
    ):
        super().__init__(hub.main_window)
        self.setWindowTitle("Text")
        self.setModal(True)
        self.dialog_layout = QVBoxLayout(self)

        self.text_layout = QHBoxLayout()
        self.text_label = QLabel("Text:")
        self.text_layout.addWidget(self.text_label)
        self.text_edit = QLineEdit(element.text())
        self.text_layout.addWidget(self.text_edit)
        self.dialog_layout.addLayout(self.text_layout)

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

    def showEvent(self, event):
        """Override showEvent to select all text when dialog appears."""
        super().showEvent(event)
        if self.text_edit.text() == "<text>":
            self.text_edit.selectAll()
            self.text_edit.setFocus()

    def getChoice(self : Self) -> tuple[str, QuillPrefChange]:
        text = self.text_edit.text()
        appearance = self.appearance_layout.getChoice()
        return text, appearance
