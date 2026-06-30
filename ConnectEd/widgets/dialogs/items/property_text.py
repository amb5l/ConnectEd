from typing import Self, Any

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QLabel, QLineEdit, QTextEdit

from ....core.check import checked
from ....core.types import NoChange, HandleId, DataKind

from ..components.group_box.property import PropertyGroupBox

from ...graphics.items.property_text import PropertyTextItem

from .text import BaseTextItemDialog


class PropertyTextItemDialog(BaseTextItemDialog):
    _TITLE = "Property Text"

    _top_section : PropertyGroupBox

    @checked
    def initTopSection(self : Self, item : PropertyTextItem) -> None:
        name = item.name()
        if not isinstance(name, str):
            raise TypeError("Bad name")
        self._top_section = PropertyGroupBox(item, name)
        self._layout.addWidget(self._top_section)

    @checked
    def getName(self : Self) -> str | NoChange:
        return self._top_section.getName()

    @checked
    def getKind(self : Self) -> DataKind | NoChange:
        return self._top_section.getKind()

    @checked
    def getValue(self : Self) -> Any | NoChange:
        return self._top_section.getValue()

    @checked
    def getCleat(self : Self) -> HandleId | NoChange:
        return self._top_section._layout._cleat_value.value()

    @checked
    def _focusEditor(self : Self) -> None:
        value = self._top_section._layout._value_value
        if isinstance(value, QLabel):
            return
        elif isinstance(value, QLineEdit | QTextEdit):
            value.setFocus(Qt.FocusReason.OtherFocusReason)
            value.selectAll()
