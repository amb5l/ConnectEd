from typing import Self

from PyQt6.QtWidgets import QWidget, QDialog, QVBoxLayout
from PyQt6.QtGui     import QShowEvent

from ...core.check import checked
from ...core.types import NoChange

from .components.layout.text_value import TextValueLayout
from .components.layout.ok_cancel  import OkCancelLayout


class TextDialog(QDialog):
    # instance variables
    _dialog_layout    : QVBoxLayout
    _value_layout     : TextValueLayout
    _ok_cancel_layout : OkCancelLayout

    @checked
    def __init__(
        self   : Self,
        text   : str,
        block  : bool = False,
        parent : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Text")
        self.setModal(True)
        self._dialog_layout = QVBoxLayout(self)
        # value section
        self._value_layout = TextValueLayout(text, block, self)
        self._dialog_layout.addLayout(self._value_layout)
        # ok/cancel section
        self._ok_cancel_layout = OkCancelLayout(self)
        self._dialog_layout.addLayout(self._ok_cancel_layout)
        # set layout
        self.setLayout(self._dialog_layout)

    def showEvent(self : Self, event : QShowEvent) -> None:
        """Override showEvent to select all text when dialog appears."""
        super().showEvent(event)
        if self._value_layout.getText() == "<text>":
            self._value_layout._text_editor.selectAll()
            self._value_layout._text_editor.setFocus()

    @checked
    def getText(self : Self) -> str | NoChange:
        return self._value_layout.getText()

    @checked
    def getBlock(self : Self) -> bool | NoChange:
        return self._value_layout.getBlock()
