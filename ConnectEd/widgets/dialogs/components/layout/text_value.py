from typing import Self

from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, \
                            QGroupBox, QButtonGroup, \
                            QLabel, QRadioButton
from PyQt6.QtGui     import QShowEvent

from ..edit import TextLineEditor, TextBlockEditor


class TextValueLayout(QVBoxLayout):
    _value_layout        : QHBoxLayout | QVBoxLayout | None
    _value_label         : QLabel | None
    _value_edit          : TextLineEditor | TextBlockEditor | None
    _format_group_box    : QGroupBox
    _format_layout       : QHBoxLayout
    _format_button_group : QButtonGroup
    _format_line_button  : QRadioButton
    _format_block_button : QRadioButton

    def __init__(self : Self, value : str, block : bool) -> QVBoxLayout:
        super().__init__()
        self._value_layout = None
        self._value_label = None
        self._value_edit = None
        self._onFormatChange(value, block)
        self._format_group_box = QGroupBox("Format")
        self._format_line_button = QRadioButton("Line")
        self._format_line_button.setChecked(not block)
        self._format_block_button = QRadioButton("Block")
        self._format_block_button.setChecked(block)
        self._format_button_group = QButtonGroup(self)
        self._format_button_group.addButton(self._format_line_button)
        self._format_button_group.addButton(self._format_block_button)
        self._format_layout = QHBoxLayout()
        self._format_layout.addWidget(self._format_line_button)
        self._format_layout.addWidget(self._format_block_button)
        self._format_group_box.setLayout(self._format_layout)
        self.addWidget(self._format_group_box)
        self._format_button_group.buttonClicked.connect(self._onFormatChange)

    def showEvent(self : Self, event : QShowEvent) -> None:
        """Override showEvent to select all text when dialog appears."""
        super().showEvent(event)
        self._value_edit.selectAll()
        self._value_edit.setFocus()

    def getValue(self : Self) -> str:
        return self._value_edit.text()

    def getBlock(self : Self) -> bool:
        return self._format_block_button.isChecked()

    def _onFormatChange(
        self : Self,
        value : str | None = None,
        block : bool | None = None
    ) -> None:
        """Create or replace the value layout based on format."""
        # get parameters
        if block is None:
            block = self._format_block_button.isChecked()
        if value is None:
            value = self._value_edit.text()
        # remove existing layout if present
        if self._value_layout is not None:
            self._value_label.deleteLater()
            self._value_edit.deleteLater()
            self.removeItem(self._value_layout)
            self._value_layout.deleteLater()
        self._value_layout = QHBoxLayout() if not block else QVBoxLayout()
        # create new layout
        self._value_label = QLabel("Value:")
        self._value_layout.addWidget(self._value_label)
        if block:
            self._value_layout = QVBoxLayout()
            self._value_edit = TextBlockEditor(value)
        else:
            self._value_layout = QHBoxLayout()
            self._value_edit = TextLineEditor(value)
        self._value_layout.addWidget(self._value_edit)
        self.insertLayout(0, self._value_layout)
