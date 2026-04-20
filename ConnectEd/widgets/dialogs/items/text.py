from typing import Self

from PyQt6.QtCore    import Qt, QTimer
from PyQt6.QtWidgets import QWidget, QDialog, QVBoxLayout, QHBoxLayout
from PyQt6.QtGui     import QShowEvent

from ....core.check import checked
from ....core.types import NoChange, AlignH, AlignV, RectHandleId, \
                           Color, FontFamily, FontSize, FontBool

from ...graphics.items.text import TextItem

from ..components.layout.text_value          import TextValueLayout
from ..components.group_box.text_orientation import TextOrientationGroupBox
from ..components.group_box.text_align       import TextAlignGroupBox
from ..components.group_box.origin           import OriginGroupBox
from ..components.group_box.text_appearance  import TextAppearancePreviewGroupBox
from ..components.layout.ok_cancel           import OkCancelLayout


class BaseTextItemDialog(QDialog):
    _TITLE : str

    # instance variables
    _layout                : QVBoxLayout
    _middle_layout         : QHBoxLayout
    _geometry_layout       : QVBoxLayout
    _orientation_group_box : TextOrientationGroupBox
    _align_group_box       : TextAlignGroupBox
    _origin_group_box      : OriginGroupBox
    _appearance_group_box  : TextAppearancePreviewGroupBox
    _ok_cancel_layout      : OkCancelLayout

    @checked
    def __init__(
        self   : Self,
        item   : TextItem,
        parent : QWidget | None = None
    ):
        super().__init__(parent)
        self.setWindowTitle(self._TITLE)
        self.setModal(True)
        self._layout = QVBoxLayout(self)
        # top (text) section
        self.initTopSection(item)
        # middle left - rotation, alignment and origin
        self._geometry_layout = QVBoxLayout()
        self._orientation_group_box = TextOrientationGroupBox(
            item.rotation(), item.mirrorH(), item.mirrorV(), item.autoflip()
        )
        self._geometry_layout.addWidget(self._orientation_group_box)
        self._align_group_box = TextAlignGroupBox(item.alignH(), item.alignV())
        self._geometry_layout.addWidget(self._align_group_box)
        self._origin_group_box = OriginGroupBox(item.origin())
        self._geometry_layout.addWidget(self._origin_group_box)
        # middle right - appearance
        self._appearance_group_box = TextAppearancePreviewGroupBox(
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
        # middle left and right combined
        self._middle_layout = QHBoxLayout()
        self._middle_layout.addLayout(self._geometry_layout)
        self._middle_layout.addWidget(self._appearance_group_box)
        self._layout.addLayout(self._middle_layout)
        # ok/cancel section
        self._ok_cancel_layout = OkCancelLayout(self)
        self._layout.addLayout(self._ok_cancel_layout)
        # finalise
        self.setLayout(self._layout)

    def initTopSection(self : Self, item : TextItem) -> None:
        raise NotImplementedError("subclass must implement initTopSection()")

    @checked
    def showEvent(self : Self, event : QShowEvent) -> None:
        """Override showEvent to focus and select all text."""
        super().showEvent(event)
        QTimer.singleShot(0, self._focusEditor)

    @checked
    def getRotation(self : Self) -> float | NoChange:
        return self._orientation_group_box.getRotation()

    @checked
    def getMirrorH(self : Self) -> bool | NoChange:
        return self._orientation_group_box.getMirrorH()

    @checked
    def getMirrorV(self : Self) -> bool | NoChange:
        return self._orientation_group_box.getMirrorV()

    @checked
    def getAutoflip(self : Self) -> bool | NoChange:
        return self._orientation_group_box.getAutoflip()

    @checked
    def getAlignH(self : Self) -> AlignH | NoChange:
        return self._align_group_box.getAlignH()

    @checked
    def getAlignV(self : Self) -> AlignV | NoChange:
        return self._align_group_box.getAlignV()

    @checked
    def getOrigin(self : Self) -> RectHandleId | NoChange:
        return self._origin_group_box.getOrigin()

    @checked
    def getColor(self : Self) -> Color | NoChange:
        return self._appearance_group_box.getColor()

    @checked
    def getFamily(self : Self) -> FontFamily | NoChange:
        return self._appearance_group_box.getFamily()

    @checked
    def getSize(self : Self) -> FontSize | NoChange:
        return self._appearance_group_box.getSize()

    @checked
    def getBold(self : Self) -> FontBool | NoChange:
        return self._appearance_group_box.getBold()

    @checked
    def getItalic(self : Self) -> FontBool | NoChange:
        return self._appearance_group_box.getItalic()

    @checked
    def getUnderline(self : Self) -> FontBool | NoChange:
        return self._appearance_group_box.getUnderline()


class TextItemDialog(BaseTextItemDialog):
    _TITLE = "Text"

    _top_section : TextValueLayout

    def initTopSection(self : Self, item : TextItem) -> None:
        self._top_section = TextValueLayout(item.text(), item.block(), self)
        self._layout.addLayout(self._top_section)

    @checked
    def getText(self : Self) -> str | NoChange:
        return self._top_section.getText()

    @checked
    def _focusEditor(self : Self) -> None:
        self._top_section._text_editor.setFocus(Qt.FocusReason.OtherFocusReason)
        self._top_section._text_editor.selectAll()
