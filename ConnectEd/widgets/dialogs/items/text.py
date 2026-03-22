from typing import Self

from PyQt6.QtCore    import Qt, QTimer
from PyQt6.QtWidgets import QWidget, QDialog, QVBoxLayout, QHBoxLayout
from PyQt6.QtGui     import QShowEvent

from ....core.check import checked
from ....core.types import Default, NoChange, AlignH, AlignV, RectHandleId, \
                           Color, FontFamily, FontSize, FontBool

from ...graphics.items.text import TextLineItem, TextBlockItem, TextBothItem

from ..components.edit import StrEditor, TextEditor

from ..components.group_box.text_rotation   import TextRotationGroupBox
from ..components.group_box.text_align      import TextAlignGroupBox
from ..components.group_box.origin          import OriginGroupBox
from ..components.group_box.text_appearance import TextAppearancePreviewGroupBox
from ..components.layout.ok_cancel          import OkCancelLayout


class TextItemDialogMixin:
    # instance variables
    _dialog_layout        : QVBoxLayout
    _text_layout          : QHBoxLayout | QVBoxLayout
    _text_editor          : StrEditor | TextEditor
    _middle_layout        : QHBoxLayout
    _geometry_layout      : QVBoxLayout
    _rotation_group_box   : TextRotationGroupBox
    _align_group_box      : TextAlignGroupBox
    _origin_group_box     : OriginGroupBox
    _appearance_group_box : TextAppearancePreviewGroupBox
    _ok_cancel_layout     : OkCancelLayout

    def initCommon(self : Self | QDialog, item : TextBothItem) -> None:
        self.setModal(True)
        self._dialog_layout = QVBoxLayout(self)
        self._dialog_layout.addWidget(self._text_editor)
        # middle left - rotation, alignment and origin
        self._geometry_layout = QVBoxLayout()
        self._rotation_group_box = TextRotationGroupBox(item.rotation(), item.flip())
        self._geometry_layout.addWidget(self._rotation_group_box)
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
        self._dialog_layout.addLayout(self._middle_layout)
        # ok/cancel section
        self._ok_cancel_layout = OkCancelLayout(self)
        self._dialog_layout.addLayout(self._ok_cancel_layout)
        # finalise
        self.setLayout(self._dialog_layout)

    def showEvent(self : Self, event : QShowEvent):
        """Override showEvent to select all text when dialog appears."""
        super().showEvent(event)
        QTimer.singleShot(0, lambda: (
            self._text_editor.setFocus(Qt.FocusReason.PopupFocusReason),
            self._text_editor.selectAll()
        ))

    @checked
    def getText(self : Self) -> str:
        return self._text_editor.value()

    @checked
    def getRotation(self : Self) -> float:
        return self._rotation_group_box.getRotation()

    @checked
    def getFlip(self : Self) -> bool:
        return self._rotation_group_box.getFlip()

    @checked
    def getAlignH(self : Self) -> AlignH:
        return self._align_group_box.getAlignH()

    @checked
    def getAlignV(self : Self) -> AlignV:
        return self._align_group_box.getAlignV()

    @checked
    def getOrigin(self : Self) -> RectHandleId:
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


class TextLineItemDialog(TextItemDialogMixin, QDialog):
    # instance variables
    _text_editor : StrEditor

    def __init__(
        self   : Self,
        item   : TextLineItem,
        parent : QWidget | None = None
    ):
        super().__init__(parent)
        self.setWindowTitle("Text Line")
        self._text_editor = StrEditor(item.text())
        self.initCommon(item)


class TextBlockItemDialog(TextItemDialogMixin, QDialog):
    # instance variables
    _text_editor : TextEditor

    def __init__(
        self   : Self,
        item   : TextBlockItem,
        parent : QWidget | None = None
    ):
        super().__init__(parent)
        self.setWindowTitle("Text Block")
        self._text_editor = TextEditor(item.text())
        self.initCommon(item)
