__all__ = ["TextDialog"]

from typing import Self, Optional

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QDialog, QWidget, QVBoxLayout, QHBoxLayout, \
                            QLabel, QLineEdit, QPushButton

from ... import hub

from ..drawing.items import ElementMixin, TextPref, TextPrefChange

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
        element : ElementMixin
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

        initial = element.appearance.text.getPref()
        defaults = element.getDefaults()
        default = TextPref(
            color     = defaults.text.color,
            family    = defaults.text.family,
            size      = defaults.text.size,
            bold      = defaults.text.bold,
            italic    = defaults.text.italic,
            underline = defaults.text.underline
        )
        self.appearance_layout = TextAppearanceLayout(initial, default)
        self.dialog_layout.addLayout(self.appearance_layout)

        okCancelLayout(self)
        self.setLayout(self.dialog_layout)

    def getChoice(self : Self) -> tuple[str, TextPrefChange]:
        text = self.text_edit.text()
        appearance = self.appearance_layout.getChoice()
        return text, appearance
