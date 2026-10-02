from __future__ import annotations

from typing            import Self, TypeVar, Generic, ClassVar
from typing_extensions import override

from PyQt6.QtCore    import QTimer
from PyQt6.QtWidgets import QDialog, QVBoxLayout
from PyQt6.QtGui     import QShowEvent, QColor

from ....core.check    import checked
from ....core.required import required
from ....core.types    import NoChange, AlignH, AlignV, RectHandleId

from ...graphics.items.base_text import BaseTextItem
from ...graphics.items.text      import TextItem

from ..components.layout.text_value      import TextValueLayout
from ..components.layout.text_appearance import TextAppearanceLayout

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...graphics.views.diagram import DiagramView


T = TypeVar("T", bound=BaseTextItem)


class BaseTextItemDialog(QDialog, Generic[T]):
    _TITLE : ClassVar[str]

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

    @required
    def initTopSection(self : Self, _item : T) -> None:
        ...

    @override
    @checked
    def showEvent(self : Self, a0 : QShowEvent | None = None) -> None:
        """Override showEvent to focus and select all text."""
        super().showEvent(a0)
        QTimer.singleShot(0, self._focusEditor)  # pyright: ignore[reportUnknownMemberType]

    @checked
    def getRotation(self : Self) -> float | NoChange:
        return self._main_layout.getRotation()

    @checked
    def getMirrorH(self : Self) -> bool | NoChange:
        return self._main_layout.getMirrorH()

    @checked
    def getMirrorV(self : Self) -> bool | NoChange:
        return self._main_layout.getMirrorV()

    @checked
    def getAutoflip(self : Self) -> bool | NoChange:
        return self._main_layout.getAutoflip()

    @checked
    def getAlignH(self : Self) -> AlignH | NoChange:
        return self._main_layout.getAlignH()

    @checked
    def getAlignV(self : Self) -> AlignV | NoChange:
        return self._main_layout.getAlignV()

    @checked
    def getOrigin(self : Self) -> RectHandleId | NoChange:
        return self._main_layout.getOrigin()

    @checked
    def getPadLeft(self : Self) -> float | NoChange:
        return self._main_layout.getPadLeft()

    @checked
    def getPadRight(self : Self) -> float | NoChange:
        return self._main_layout.getPadRight()

    @checked
    def getPadTop(self : Self) -> float | NoChange:
        return self._main_layout.getPadTop()

    @checked
    def getPadBottom(self : Self) -> float | NoChange:
        return self._main_layout.getPadBottom()

    @checked
    def getColor(self : Self) -> QColor | None | NoChange:
        return self._main_layout.getColor()

    @checked
    def getFont(self : Self) -> str | None | NoChange:
        return self._main_layout.getFont()

    @checked
    def getSize(self : Self) -> float | None | NoChange:
        return self._main_layout.getSize()

    @checked
    def getBold(self : Self) -> bool | None | NoChange:
        return self._main_layout.getBold()

    @checked
    def getItalic(self : Self) -> bool | None | NoChange:
        return self._main_layout.getItalic()

    @checked
    def getUnderline(self : Self) -> bool | None | NoChange:
        return self._main_layout.getUnderline()

    @required
    def _focusEditor(self : Self) -> None:
        ...


class TextItemDialog(BaseTextItemDialog[TextItem]):
    _TITLE : ClassVar[str] = "Text"

    _top_section : TextValueLayout

    @override
    @checked
    def __init__(self : Self, item : TextItem, view : DiagramView) -> None:
        self._top_section = TextValueLayout(item.text(), item.block(), self)
        super().__init__(item, view)

    @override
    def initTopSection(self : Self, _item : TextItem) -> None:
        self._layout.addLayout(self._top_section)

    @checked
    def getText(self : Self) -> str | NoChange:
        return self._top_section.getText()

    @checked
    def getBlock(self : Self) -> bool | NoChange:
        return self._top_section.getBlock()

    @override
    @checked
    def _focusEditor(self : Self) -> None:
        self._top_section.focusEditor()
