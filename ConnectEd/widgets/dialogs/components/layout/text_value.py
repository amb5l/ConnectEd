from typing import Self

from PyQt6.QtCore    import QTimer
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QDialog

from .....core.check import checked
from .....core.types import NoChange

from ..edit import StrEditor, TextEditor

from ..combo.text_format import TextFormatComboBox

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...items.text import TextItemDialog


class TextValueLayout(QVBoxLayout):
    _dialog             : "TextItemDialog"
    _text_format_layout : QHBoxLayout
    _text_format_label  : QLabel
    _text_format_combo  : TextFormatComboBox
    _text_editor        : StrEditor | TextEditor

    @checked
    def __init__(self : Self, text : str, block : bool, dialog : QDialog) -> None:
        super().__init__()
        self._dialog = dialog
        self._text_format_layout = QHBoxLayout()
        self._text_format_label = QLabel("Format:")
        self._text_format_layout.addWidget(self._text_format_label)
        self._text_format_combo = TextFormatComboBox(block)
        self._text_format_combo.activated.connect(self._onTextFormatChange)
        self._text_format_layout.addWidget(self._text_format_combo)
        self._text_format_layout.addStretch(1)
        self.addLayout(self._text_format_layout)
        editor_cls = TextEditor if block else StrEditor
        self._text_editor = editor_cls(text)
        self.addWidget(self._text_editor)

    @checked
    def getText(self : Self) -> str | NoChange:
        return self._text_editor.value()

    @checked
    def getBlock(self : Self) -> bool | NoChange:
        return self._text_format_combo.value()

    @checked
    def _onTextFormatChange(self : Self) -> None:
        text = self._text_editor.text()
        block = self._text_format_combo.raw()
        self.removeWidget(self._text_editor)
        self._text_editor.deleteLater()
        editor_cls = TextEditor if block else StrEditor
        self._text_editor = editor_cls(text)
        self.insertWidget(1, self._text_editor)
        QTimer.singleShot(0, lambda: self._dialog.resize(self._dialog.sizeHint()))
