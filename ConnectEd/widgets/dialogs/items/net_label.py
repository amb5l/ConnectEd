from typing import Self

from PyQt6.QtCore import Qt

from ....core.check import checked
from ....core.types import NoChange

from ...graphics.items.net_label import NetLabelItem

from ..components.group_box.net_label import NetLabelItemGroupBox

from .text import BaseTextItemDialog


class NetLabelItemDialog(BaseTextItemDialog[NetLabelItem]):
    _TITLE = "Net Label"

    _top_section : NetLabelItemGroupBox

    @checked
    def initTopSection(self : Self, item : NetLabelItem) -> None:
        self._top_section = NetLabelItemGroupBox(item.name(), item.value())
        self._layout.addWidget(self._top_section)

    @checked
    def getName(self : Self) -> str | NoChange:
        return self._top_section.getName()

    @checked
    def getValue(self : Self) -> str | NoChange:
        return self._top_section.getValue()

    @checked
    def _focusEditor(self : Self) -> None:
        value = self._top_section._layout._value_value
        value.setFocus(Qt.FocusReason.OtherFocusReason)
        value.selectAll()
