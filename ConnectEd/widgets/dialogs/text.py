from typing import Self

from PyQt6.QtWidgets import QWidget, QDialog, QVBoxLayout
from PyQt6.QtGui     import QShowEvent, QColor

from ..graphics.items import Default, NoChange

from ..graphics.items.unitext import UniText

from .components.layout.text_value      import TextValueLayout
from .components.layout.text_appearance import TextAppearancePreviewLayout
from .components.layout.ok_cancel       import OkCancelLayout


class TextValueDialog(QDialog):
    # instance variables
    _dialog_layout     : QVBoxLayout
    _value_layout      : TextValueLayout
    _ok_cancel_layout  : OkCancelLayout

    def __init__(
        self   : Self,
        text   : str,
        block  : bool,
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
            self._value_layout._value_edit.selectAll()
            self._value_layout._value_edit.setFocus()

    def getText(self : Self) -> str:
        return self._value_layout.getValue()

    def getBlock(self : Self) -> bool:
        return self._value_layout.getBlock()


class TextItemDialog(QDialog):
    # instance variables
    _dialog_layout     : QVBoxLayout
    _value_layout      : TextValueLayout
    _appearance_layout : TextAppearancePreviewLayout
    _ok_cancel_layout  : OkCancelLayout

    def __init__(
        self   : Self,
        item   : UniText,
        parent : QWidget | None = None
    ):
        super().__init__(parent)
        self.setWindowTitle("Text")
        self.setModal(True)
        self._dialog_layout = QVBoxLayout(self)
        # value section
        self._value_layout = TextValueLayout(item.text(), item.block())
        self._dialog_layout.addLayout(self._value_layout)
        # appearance section
        self._appearance_layout = TextAppearancePreviewLayout(
            item.quillColor(),
            item.quillFamily(),
            item.quillSize(),
            item.quillBold(),
            item.quillItalic(),
            item.quillUnderline(),
            item.defaultQuillColor(),
            item.defaultQuillFamily(),
            item.defaultQuillSize(),
            item.defaultQuillBold(),
            item.defaultQuillItalic(),
            item.defaultQuillUnderline()
        )
        self._dialog_layout.addLayout(self._appearance_layout)
        # ok/cancel section
        self._ok_cancel_layout = OkCancelLayout(self)
        self._dialog_layout.addLayout(self._ok_cancel_layout)
        # set layout
        self.setLayout(self._dialog_layout)

    def showEvent(self : Self, event : QShowEvent):
        """Override showEvent to select all text when dialog appears."""
        super().showEvent(event)
        if self._value_layout.getValue() == "<text>":
            self._value_layout._value_edit.selectAll()
            self._value_layout._value_edit.setFocus()

    def getText(self : Self) -> str:
        return self._value_layout.getValue()

    def getBlock(self : Self) -> bool:
        return self._value_layout.getBlock()

    def getColor(self : Self) -> QColor | Default | NoChange:
        return self._appearance_layout.getColor()

    def getFamily(self : Self) -> str | Default | NoChange:
        return self._appearance_layout.getFamily()

    def getSize(self : Self) -> float | NoChange | Default:
        return self._appearance_layout.getSize()

    def getBold(self : Self) -> bool | Default | NoChange:
        return self._appearance_layout.getBold()

    def getItalic(self : Self) -> bool | Default | NoChange:
        return self._appearance_layout.getItalic()

    def getUnderline(self : Self) -> bool | Default | NoChange:
        return self._appearance_layout.getUnderline()
