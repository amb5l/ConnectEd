from typing import Self, Any

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QLabel, QLineEdit, QTextEdit

from ...core.check import checked
from ...core.types import NoChange, HandleId, DataKind

from ..graphics.items.property_text import PropertyTextItem

from .components.group_box.property import PropertyGroupBox

from .items.text import BaseTextItemDialog


class PropertyDialog(BaseTextItemDialog):
    _TITLE = "Property"

    _top_section : PropertyGroupBox

    @checked
    def initTopSection(self : Self, item : PropertyTextItem) -> None:
        self._top_section = PropertyGroupBox(item, item.name())
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
    def getRotation(self : Self) -> float | NoChange:
        if self._main_layout.isEnabled():
            return self._main_layout._orientation_group_box.getRotation()

    @checked
    def getMirrorH(self : Self) -> bool | NoChange:
        return self._main_layout._orientation_group_box.getMirrorH()

    @checked
    def getMirrorV(self : Self) -> bool | NoChange:
        return self._main_layout._orientation_group_box.getMirrorV()

    @checked
    def getAutoflip(self : Self) -> bool | NoChange:
        return self._main_layout._orientation_group_box.getAutoflip()

    @checked
    def getAlignH(self : Self) -> AlignH | NoChange:
        return self._main_layout._align_group_box.getAlignH()

    @checked
    def getAlignV(self : Self) -> AlignV | NoChange:
        return self._main_layout._align_group_box.getAlignV()

    @checked
    def getOrigin(self : Self) -> RectHandleId | NoChange:
        return self._main_layout._origin_group_box.getOrigin()

    @checked
    def getPadLeft(self : Self) -> float | NoChange:
        return self._main_layout._padding_group_box.getPadLeft()

    @checked
    def getPadRight(self : Self) -> float | NoChange:
        return self._main_layout._padding_group_box.getPadRight()

    @checked
    def getPadTop(self : Self) -> float | NoChange:
        return self._main_layout._padding_group_box.getPadTop()

    @checked
    def getPadBottom(self : Self) -> float | NoChange:
        return self._main_layout._padding_group_box.getPadBottom()

    @checked
    def getColor(self : Self) -> QColor | NoChange:
        return self._main_layout._typography_group_box.getColor()

    @checked
    def getFont(self : Self) -> str | NoChange:
        return self._main_layout._typography_group_box.getFont()

    @checked
    def getSize(self : Self) -> float | NoChange:
        return self._main_layout._typography_group_box.getSize()

    @checked
    def getBold(self : Self) -> bool | NoChange:
        return self._main_layout._typography_group_box.getBold()

    @checked
    def getItalic(self : Self) -> bool | NoChange:
        return self._main_layout._typography_group_box.getItalic()

    @checked
    def getUnderline(self : Self) -> bool | NoChange:
        return self._main_layout._typography_group_box.getUnderline()


    @checked
    def _focusEditor(self : Self) -> None:
        if isinstance(value := self._top_section._layout._value_value, QLabel):
            return
        elif isinstance(value, QLineEdit | QTextEdit):
            value.setFocus(Qt.FocusReason.OtherFocusReason)
            value.selectAll()
