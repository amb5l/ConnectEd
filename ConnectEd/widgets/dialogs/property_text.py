from typing import Self

from PyQt6.QtWidgets import QWidget, QDialog, \
                            QVBoxLayout, QHBoxLayout, QGroupBox, \
                            QButtonGroup, QRadioButton
from PyQt6.QtGui     import QShowEvent, QColor

from ..graphics.items.property_text import PropertyTextItem

from .components.layout.text_value      import TextValueLayout
from .components.layout.text_appearance import TextAppearancePreviewLayout
from .components.layout.ok_cancel       import OkCancelLayout


class PropertyTextDialog(QDialog):
    _dialog_layout     : QVBoxLayout
    _value_layout      : TextValueLayout
    _appearance_layout : TextAppearancePreviewLayout
    _ok_cancel_layout  : OkCancelLayout

    def __init__(
        self   : Self,
        item   : PropertyTextItem,
        parent : QWidget | None = None # not to be confused with _parent
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"Property Text: {item.property()}")
        self.setModal(True)
        self._dialog_layout = QVBoxLayout(self)
        # value section
        self._value_layout = TextValueLayout(item.value(), item.block())
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

    def getValue(self : Self) -> str:
        return self._value_edit.text()

    def getBlock(self : Self) -> bool:
        return self._format_block_button.isChecked()

    def getColor(self : Self) -> QColor:
        return self._appearance_layout.getColor()

    def getFamily(self : Self) -> str:
        return self._appearance_layout.getFamily()

    def getSize(self : Self) -> float:
        return self._appearance_layout.getSize()

    def getBold(self : Self) -> bool:
        return self._appearance_layout.getBold()

    def getItalic(self : Self) -> bool:
        return self._appearance_layout.getItalic()

    def getUnderline(self : Self) -> bool:
        return self._appearance_layout.getUnderline()
