from typing import Self

from PyQt6.QtCore    import Qt, QTimer
from PyQt6.QtWidgets import QWidget, QDialog, QVBoxLayout, QHBoxLayout
from PyQt6.QtGui     import QShowEvent, QColor

from ....core.check import checked
from ....core.types import Default, NoChange, AlignH, AlignV, RectHandleId

from ...graphics.items.text import TextItem

from ..components.edit import TextLineEditor, TextBlockEditor

from ..components.group_box.text_format     import TextFormatGroupBox
from ..components.group_box.rotation        import RotationGroupBox
from ..components.group_box.text_align      import TextAlignGroupBox
from ..components.group_box.origin          import OriginGroupBox
from ..components.group_box.text_appearance import TextAppearancePreviewGroupBox
from ..components.layout.ok_cancel          import OkCancelLayout


class TextItemDialogMixin:
    # instance variables
    _dialog_layout          : QVBoxLayout
    _format_rotation_layout : QHBoxLayout
    _format_group_box       : TextFormatGroupBox
    _rotation_group_box     : RotationGroupBox
    _middle_layout          : QHBoxLayout
    _align_origin_layout    : QVBoxLayout
    _align_group_box        : TextAlignGroupBox
    _origin_group_box       : OriginGroupBox
    _appearance_group_box   : TextAppearancePreviewGroupBox
    _ok_cancel_layout       : OkCancelLayout

    def initCommon(self : Self | QDialog, item : TextItem) -> None:
        # format and rotation
        self._format_rotation_layout = QHBoxLayout()
        self._format_group_box = TextFormatGroupBox(item.block(), self)
        self._format_rotation_layout.addWidget(self._format_group_box)
        self._rotation_group_box = RotationGroupBox(item.rotation(), item.rotComp())
        self._format_rotation_layout.addWidget(self._rotation_group_box)
        self._dialog_layout.addLayout(self._format_rotation_layout)
        # middle left - alignment and origin
        self._align_origin_layout = QVBoxLayout()
        self._align_group_box = TextAlignGroupBox(item.alignH(), item.alignV())
        self._align_origin_layout.addWidget(self._align_group_box)
        self._origin_group_box = OriginGroupBox(item.origin())
        self._align_origin_layout.addWidget(self._origin_group_box)
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
        # middle
        self._middle_layout = QHBoxLayout()
        self._middle_layout.addLayout(self._align_origin_layout)
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
    def getRotAngle(self : Self) -> float:
        return self._rotation_group_box.getRotAngle()

    @checked
    def getRotComp(self : Self) -> bool:
        return self._rotation_group_box.getRotComp()

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
    def getColor(self : Self) -> QColor | Default | NoChange:
        return self._appearance_group_box.getColor()

    @checked
    def getFamily(self : Self) -> str | Default | NoChange:
        return self._appearance_group_box.getFamily()

    @checked
    def getSize(self : Self) -> float | Default | NoChange:
        return self._appearance_group_box.getSize()

    @checked
    def getBold(self : Self) -> bool | Default | NoChange:
        return self._appearance_group_box.getBold()

    @checked
    def getItalic(self : Self) -> bool | Default | NoChange:
        return self._appearance_group_box.getItalic()

    @checked
    def getUnderline(self : Self) -> bool | Default | NoChange:
        return self._appearance_group_box.getUnderline()


class TextItemDialog(TextItemDialogMixin, QDialog):
    # instance variables
    _dialog_layout          : QVBoxLayout
    _text_editor            : TextLineEditor | TextBlockEditor
    _format_rotation_layout : QHBoxLayout
    _format_group_box       : TextFormatGroupBox
    _rotation_group_box     : RotationGroupBox
    _middle_layout          : QHBoxLayout
    _align_origin_layout    : QVBoxLayout
    _align_group_box        : TextAlignGroupBox
    _origin_group_box       : OriginGroupBox
    _appearance_group_box   : TextAppearancePreviewGroupBox
    _ok_cancel_layout       : OkCancelLayout

    def __init__(
        self   : Self,
        item   : TextItem,
        parent : QWidget | None = None
    ):
        super().__init__(parent)
        self.setWindowTitle("Text")
        self.setModal(True)
        self._dialog_layout = QVBoxLayout(self)
        self._onFormatChange(item.block(), item.text())
        self.initCommon(item)
        self._format_group_box.formatChanged.connect(self._onFormatChange)

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
    def getBlock(self : Self) -> bool:
        return self._format_group_box.getBlock()

    def _onFormatChange(
        self  : Self,
        block : bool | None = None,
        text  : str | None = None
    ) -> None:
        block = self.getBlock() if block is None else block
        if hasattr(self, '_text_editor'):
            text = self._text_editor.value()
            self._text_editor.hide()
            self._text_editor.deleteLater()
            self._dialog_layout.removeWidget(self._text_editor)
        self._text_editor = TextBlockEditor(text) if block else TextLineEditor(text)
        self._dialog_layout.insertWidget(0, self._text_editor)
        self.layout().invalidate()
        self.layout().activate()
        self.resize(self.sizeHint())
