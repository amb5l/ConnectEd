from typing import Self, Protocol

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, \
                            QGroupBox, QButtonGroup, QRadioButton, QLabel
from PyQt6.QtGui     import QShowEvent

from ..edit import TextLineEditor, TextBlockEditor


class ParentProtocol(Protocol):
    _value_layout  : "TextValueLayout"
    _format_layout : "TextFormatLayout"


class TextValueLayout(QVBoxLayout):
    _layout : QHBoxLayout | QVBoxLayout | None
    _label  : QLabel | None
    _edit   : TextLineEditor | TextBlockEditor | None

    def __init__(self : Self, value : str) -> QVBoxLayout:
        super().__init__()
        self._layout = None
        self._label = None
        self._edit = None

    def showEvent(self : Self, event : QShowEvent) -> None:
        """Override showEvent to select all text when dialog appears."""
        super().showEvent(event)
        self._edit.selectAll()
        self._edit.setFocus()

    def getValue(self : Self) -> str:
        return self._edit.text()


class TextFormatLayout(QVBoxLayout):
    _parent       : QDialog | ParentProtocol | None
    _group_box    : QGroupBox
    _layout       : QHBoxLayout
    _button_group : QButtonGroup
    _line_button  : QRadioButton
    _block_button : QRadioButton

    def __init__(
        self   : Self,
        block  : bool,
        parent : QDialog | ParentProtocol | None = None
    ) -> QVBoxLayout:
        super().__init__()
        self._parent = parent
        self._group_box = QGroupBox("Format")
        self._line_button = QRadioButton("Line")
        self._line_button.setChecked(not block)
        self._block_button = QRadioButton("Block")
        self._block_button.setChecked(block)
        self._button_group = QButtonGroup(self)
        self._button_group.addButton(self._line_button)
        self._button_group.addButton(self._block_button)
        self._layout = QHBoxLayout()
        self._layout.addWidget(self._line_button)
        self._layout.addWidget(self._block_button)
        self._group_box.setLayout(self._layout)
        self.addWidget(self._group_box)
        self._button_group.buttonClicked.connect(lambda _: self.onFormatChange())

    def showEvent(self : Self, event : QShowEvent) -> None:
        """Override showEvent to select all text when dialog appears."""
        super().showEvent(event)
        self._value_edit.selectAll()
        self._value_edit.setFocus()

    def getValue(self : Self) -> str:
        return self._value_edit.text()

    def getBlock(self : Self) -> bool:
        return self._block_button.isChecked()

    def onFormatChange(self : Self, block : bool | None = None) -> None:
        """Create or replace the value layout based on format."""
        # get parameters
        block = block or self._block_button.isChecked()
        value = self._parent._value_layout._edit.text() \
            if self._parent._value_layout._edit else ""
        # remove existing layout if present
        if self._parent._value_layout._layout is not None:
            self._parent._value_layout._label.deleteLater()
            self._parent._value_layout._edit.deleteLater()
            self.removeItem(self._parent._value_layout._layout)
            self._parent._value_layout._layout.deleteLater()
        # create new layout
        self._parent._value_layout._layout = QVBoxLayout() if block else QHBoxLayout()
        self._parent._value_layout._label = QLabel("Value:")
        self._parent._value_layout._edit = \
            TextBlockEditor(value) if block else TextLineEditor(value)
        self._parent._value_layout._layout.addWidget(self._parent._value_layout._label)
        self._parent._value_layout._layout.addWidget(self._parent._value_layout._edit)
        self._parent._value_layout.insertLayout(0, self._parent._value_layout._layout)
        # resize
        self._parent.layout().invalidate()
        self._parent.layout().activate()
        self._parent.resize(self._parent.sizeHint())
