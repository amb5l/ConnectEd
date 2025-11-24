from typing import Self
from abc    import abstractmethod

from PyQt6.QtWidgets import QWidget, QDialog, QVBoxLayout, QHBoxLayout, \
                            QLabel, QPushButton
from PyQt6.QtGui     import QShowEvent

from ..graphics.items import QuillPref, QuillPrefChange

from ..graphics.items.base_text import BaseTextMixin

from .components.line_edit              import LineEdit
from .components.text_edit              import TextEdit
from .components.layout.text_appearance import TextAppearanceLayout
from .components.layout.ok_cancel       import okCancelLayout


class TextDialogMixin:
    _text_layout       : QVBoxLayout | QHBoxLayout
    _text_label        : QLabel
    _text_edit         : LineEdit | TextEdit
    _appearance_layout : TextAppearanceLayout
    _ok_cancel_layout  : QHBoxLayout
    _ok_button         : QPushButton
    _cancel_button     : QPushButton

    def __init__(
        self   : Self,
        item   : BaseTextMixin,
        parent : QWidget | None = None
    ):
        super().__init__(parent)
        self.setWindowTitle("Text")
        self.setModal(True)
        self._dialog_layout = QVBoxLayout(self)
        self.initTextLayout(item)
        self.initAppearanceLayout(item)
        okCancelLayout(self)
        self.setLayout(self._dialog_layout)

    @abstractmethod
    def initTextLayout(self : Self, item : BaseTextMixin) -> None:
        ...

    def initAppearanceLayout(self : Self, item : BaseTextMixin) -> None:
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

    def showEvent(self : Self, event : QShowEvent):
        """Override showEvent to select all text when dialog appears."""
        super().showEvent(event)
        if self._text_edit.text() == "<text>":
            self._text_edit.selectAll()
            self._text_edit.setFocus()

    def getChoice(self : Self) -> tuple[str, QuillPrefChange]:
        text = self._text_edit.text()
        appearance = self._appearance_layout.getChoice()
        return text, appearance


class TextLineDialog(TextDialogMixin, QDialog):
    _dialog_layout : QVBoxLayout
    _text_layout   : QHBoxLayout
    _text_label    : QLabel
    _text_edit     : LineEdit

    def initTextLayout(self : Self, item : BaseTextMixin) -> None:
        self._text_layout = QHBoxLayout()
        self._text_label = QLabel("Text:")
        self._text_layout.addWidget(self._text_label)
        self._text_edit = LineEdit(item.text())
        self._text_layout.addWidget(self._text_edit)
        self._dialog_layout.addLayout(self._text_layout)


class TextBlockDialog(QDialog):
    _dialog_layout : QVBoxLayout
    _text_layout   : QVBoxLayout
    _text_label    : QLabel
    _text_edit     : TextEdit

    def initTextLayout(self : Self, item : BaseTextMixin) -> None:
        self._text_layout = QVBoxLayout()
        self._text_label = QLabel("Text:")
        self._text_layout.addWidget(self._text_label)
        self._text_edit = TextEdit(item.text())
        self._text_layout.addWidget(self._text_edit)
        self._dialog_layout.addLayout(self._text_layout)
