from typing import Self, Protocol

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, \
                            QGroupBox, QButtonGroup, QRadioButton, QLabel

from ..edit import TextLineEditor, TextBlockEditor


class ParentProtocol(Protocol):
    _value_layout  : "TextValueLayout"
    _format_layout : "TextFormatLayout"


class TextValueLayout(QVBoxLayout):
    _layout : QHBoxLayout | QVBoxLayout | None
    _label  : QLabel | None
    _edit   : TextLineEditor | TextBlockEditor | None

    def __init__(self : Self) -> QVBoxLayout:
        super().__init__()
        self._layout = None
        self._label = None
        self._edit = None

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

    def getValue(self : Self) -> str:
        return self._value_edit.text()

    def getBlock(self : Self) -> bool:
        return self._block_button.isChecked()

    def onFormatChange(self : Self, block : bool | None = None) -> None:
        """Create or replace the value layout based on format."""
        vl = self._parent._value_layout
        # get parameters
        block = block or self._block_button.isChecked()
        value = vl._edit.text() if vl._edit else ""
        # remove existing layout if present
        if vl._layout is not None:
            vl._label.hide()
            vl._edit.hide()
            vl._label.deleteLater()
            vl._edit.deleteLater()
            vl.removeItem(vl._layout)
            vl._layout.deleteLater()
        # create new layout
        vl._layout = QVBoxLayout() if block else QHBoxLayout()
        vl._label = QLabel("Value:")
        vl._edit = TextBlockEditor(value) if block else TextLineEditor(value)
        vl._layout.addWidget(vl._label)
        vl._layout.addWidget(vl._edit)
        vl.insertLayout(0, vl._layout)
        # resize
        self._parent.layout().invalidate()
        self._parent.layout().activate()
        self._parent.resize(self._parent.sizeHint())
