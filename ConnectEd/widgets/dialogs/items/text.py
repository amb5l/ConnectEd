from typing import Self

from PyQt6.QtCore    import Qt, QTimer
from PyQt6.QtWidgets import QWidget, QDialog, QVBoxLayout, QHBoxLayout, \
                            QGroupBox, QCheckBox
from PyQt6.QtGui     import QShowEvent, QColor

from ....core.check import checked
from ....core.types import Default, NoChange, AlignH, AlignV, RectHandleId

from ...graphics.items.text import TextItem

from ..components.layout.text_value         import TextValueLayout, TextFormatLayout
from ..components.group_box.text_align      import TextAlignGroupBox
from ..components.group_box.origin          import OriginGroupBox
from ..components.group_box.text_appearance import TextAppearancePreviewGroupBox
from ..components.layout.ok_cancel          import OkCancelLayout


class TextItemDialog(QDialog):
    # instance variables
    _dialog_layout        : QVBoxLayout
    _value_layout         : TextValueLayout
    _fr_layout            : QHBoxLayout
    _format_layout        : TextFormatLayout
    _rotcomp_group_box    : QGroupBox
    _rotcomp_layout       : QVBoxLayout
    _rotcomp_checkbox     : QCheckBox
    _middle_layout        : QHBoxLayout
    _align_origin_layout  : QVBoxLayout
    _align_group_box      : TextAlignGroupBox
    _origin_group_box     : OriginGroupBox
    _appearance_group_box : TextAppearancePreviewGroupBox
    _ok_cancel_layout     : OkCancelLayout

    def __init__(
        self   : Self,
        item   : TextItem,
        parent : QWidget | None = None
    ):
        super().__init__(parent)
        self.setWindowTitle("Text")
        self.setModal(True)
        self._dialog_layout = QVBoxLayout(self)
        ########################################################################
        # value
        ########################################################################
        # value section
        self._value_layout = TextValueLayout()
        self._dialog_layout.addLayout(self._value_layout)
        ########################################################################
        # format and rotation compensation
        ########################################################################
        self._fr_layout = QHBoxLayout()
        # format section
        self._format_layout = TextFormatLayout(item.block(), self)
        self._fr_layout.addLayout(self._format_layout)
        # rotation compensation section
        self._rotcomp_group_box = QGroupBox("Rotation Compensation")
        self._rotcomp_layout = QVBoxLayout()
        self._rotcomp_checkbox = QCheckBox("Enable")
        self._rotcomp_checkbox.setChecked(item.rotcomp())
        self._rotcomp_layout.addWidget(self._rotcomp_checkbox)
        self._rotcomp_group_box.setLayout(self._rotcomp_layout)
        self._fr_layout.addWidget(self._rotcomp_group_box)
        # done
        self._dialog_layout.addLayout(self._fr_layout)
        ########################################################################
        # middle left - alignment and origin
        ########################################################################
        self._align_origin_layout = QVBoxLayout()
        self._align_group_box = TextAlignGroupBox(item.alignH(), item.alignV())
        self._align_origin_layout.addWidget(self._align_group_box)
        self._origin_group_box = OriginGroupBox(item.origin())
        self._align_origin_layout.addWidget(self._origin_group_box)
        ########################################################################
        # middle right - appearance
        ########################################################################
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
        ########################################################################
        # middle
        ########################################################################
        self._middle_layout = QHBoxLayout()
        self._middle_layout.addLayout(self._align_origin_layout)
        self._middle_layout.addWidget(self._appearance_group_box)
        self._dialog_layout.addLayout(self._middle_layout)
        ########################################################################
        # bottom
        ########################################################################
        # ok/cancel section
        self._ok_cancel_layout = OkCancelLayout(self)
        self._dialog_layout.addLayout(self._ok_cancel_layout)
        ########################################################################
        # finalise
        ########################################################################
        self.setLayout(self._dialog_layout)
        self._format_layout.onFormatChange()           # initialise format
        self._value_layout._edit.setText(item.text())  # initialise value

    def showEvent(self : Self, event : QShowEvent):
        """Override showEvent to select all text when dialog appears."""
        super().showEvent(event)
        QTimer.singleShot(0, lambda: (
            self._value_layout._edit.setFocus(Qt.FocusReason.PopupFocusReason),
            self._value_layout._edit.selectAll()
        ))

    @checked
    def getText(self : Self) -> str:
        return self._value_layout.getValue()

    @checked
    def getBlock(self : Self) -> bool:
        return self._format_layout.getBlock()

    @checked
    def getRotcomp(self : Self) -> bool:
        return self._rotcomp_checkbox.isChecked()

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
