from typing import Self

from PyQt6.QtCore    import pyqtSignal
from PyQt6.QtWidgets import QWidget, QDialog, QGroupBox, QHBoxLayout, \
                            QButtonGroup, QRadioButton


class TextFormatGroupBox(QGroupBox):
    _dialog       : QDialog | None
    _layout       : QHBoxLayout
    _button_group : QButtonGroup
    _line_button  : QRadioButton
    _block_button : QRadioButton

    formatChanged = pyqtSignal(bool)  # noqa N815

    def __init__(
        self   : Self,
        block  : bool,
        dialog : QDialog | None = None,
        parent : QWidget | None = None
    ) -> None:
        super().__init__("Format", parent)
        self._dialog = dialog
        self._layout = QHBoxLayout()
        self._button_group = QButtonGroup(self)
        self._line_button = QRadioButton("Line")
        self._line_button.setChecked(not block)
        self._button_group.addButton(self._line_button)
        self._block_button = QRadioButton("Block")
        self._block_button.setChecked(block)
        self._button_group.addButton(self._block_button)
        self._layout.addWidget(self._line_button)
        self._layout.addWidget(self._block_button)
        self.setLayout(self._layout)
        self._button_group.buttonClicked.connect(self._onButtonClicked)

    def _onButtonClicked(self : Self, button : QRadioButton) -> None:
        if button == self._line_button:
            self.formatChanged.emit(False)
        elif button == self._block_button:
            self.formatChanged.emit(True)

    def getBlock(self : Self) -> bool:
        return self._block_button.isChecked()
