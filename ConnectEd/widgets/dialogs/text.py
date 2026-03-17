from typing import Self

from PyQt6.QtWidgets import QWidget, QDialog, QVBoxLayout
from PyQt6.QtGui     import QShowEvent

from .components.layout.text_value import TextValueLayout
from .components.layout.ok_cancel  import OkCancelLayout


class TextDialog(QDialog):
    # instance variables
    _dialog_layout    : QVBoxLayout
    _value_layout     : TextValueLayout
    _format_group_box : TextFormatGroupBox
    _ok_cancel_layout : OkCancelLayout

    def __init__(
        self   : Self,
        text   : Text,
        parent : QWidget | None = None
    ):
        super().__init__(parent)
        self.setWindowTitle("Text")
        self.setModal(True)
        self._dialog_layout = QVBoxLayout(self)
        # value section
        self._value_layout = TextValueLayout(text, block)
        self._dialog_layout.addLayout(self._value_layout)
        # ok/cancel section
        self._ok_cancel_layout = OkCancelLayout(self)
        self._dialog_layout.addLayout(self._ok_cancel_layout)
        # set layout
        self.setLayout(self._dialog_layout)

    def showEvent(self : Self, event : QShowEvent):
        """Override showEvent to select all text when dialog appears."""
        super().showEvent(event)
        if self._value_layout.getValue() == "<text>":
            self._value_layout._edit.selectAll()
            self._value_layout._edit.setFocus()

    def getText(self : Self) -> str:
        return self._value_layout.getValue()

    def getBlock(self : Self) -> bool:
        return self._value_layout.getBlock()


