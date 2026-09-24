from __future__ import annotations

from typing import Self, TypeVar, Generic

from PyQt6.QtCore    import Qt, QTimer
from PyQt6.QtWidgets import QDialog, QVBoxLayout
from PyQt6.QtGui     import QShowEvent, QColor

from ....core.check import checked
from ....core.types import NoChange, AlignH, AlignV, RectHandleId

from ...graphics.items.text import BaseTextItem, TextItem

from ..components.layout.text_value import TextValueLayout

from ..components.layout.text_appearance import TextAppearanceLayout


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...graphics.views.diagram import DiagramView


T = TypeVar("T", bound=BaseTextItem)


class BaseTextItemDialog(QDialog, Generic[T]):
    _TITLE : str

    # instance variables
    _layout      : QVBoxLayout
    _main_layout : TextAppearanceLayout

    @checked
    def __init__(
        self : Self,
        item : T,
        view : DiagramView
    ):
        super().__init__(view)
        self.setWindowTitle(self._TITLE)
        self.setModal(True)
        self._layout = QVBoxLayout(self)
        self.initTopSection(item)
        self._main_layout = TextAppearanceLayout(item, self, view)
        self._layout.addLayout(self._main_layout)

    def initTopSection(self : Self, item) -> None:
        raise NotImplementedError("subclass must implement initTopSection()")

    @checked
    def showEvent(self : Self, a0 : QShowEvent | None = None) -> None:
        """Override showEvent to focus and select all text."""
        super().showEvent(a0)
        QTimer.singleShot(0, self._focusEditor)

    @checked
    def getRotation(self : Self) -> float | NoChange:
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
        raise NotImplementedError("subclass must implement _focusEditor()")


class TextItemDialog(BaseTextItemDialog[TextItem]):
    _TITLE = "Text"

    _top_section : TextValueLayout

    def initTopSection(self : Self, item : TextItem) -> None:
        self._top_section = TextValueLayout(item.text(), item.block(), self)
        self._layout.addLayout(self._top_section)

    @checked
    def getText(self : Self) -> str | NoChange:
        return self._top_section.getText()

    @checked
    def getBlock(self : Self) -> bool | NoChange:
        return self._top_section.getBlock()

    @checked
    def _focusEditor(self : Self) -> None:
        self._top_section._text_editor.setFocus(Qt.FocusReason.OtherFocusReason)
        self._top_section._text_editor.selectAll()
