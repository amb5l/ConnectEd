from typing import Self

from PyQt6.QtCore    import Qt, QTimer
from PyQt6.QtWidgets import QWidget, QDialog, QVBoxLayout, QHBoxLayout, \
                            QGroupBox, QCheckBox
from PyQt6.QtGui     import QShowEvent, QColor

from ...graphics.items import Default, NoChange, AlignH, AlignV

from ...graphics.items.unitext import UniTextItem

from ..components.layout.text_value      import TextValueLayout, TextFormatLayout
from ..components.layout.text_align      import TextAlignLayout
from ..components.layout.origin          import OriginLayout
from ..components.layout.text_appearance import TextAppearancePreviewLayout
from ..components.layout.ok_cancel       import OkCancelLayout


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
    _left_layout          : QVBoxLayout
    _align_group_box      : QGroupBox
    _align_layout         : TextAlignLayout
    _origin_group_box     : QGroupBox
    _origin_layout        : OriginLayout
    _right_layout         : QVBoxLayout
    _appearance_group_box : QGroupBox
    _appearance_layout    : TextAppearancePreviewLayout
    _ok_cancel_layout     : OkCancelLayout

    def __init__(
        self   : Self,
        item   : UniTextItem,
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
        self._value_layout = TextValueLayout(item.text())
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
        # middle left
        ########################################################################
        self._left_layout = QVBoxLayout()
        # align section
        self._align_group_box = QGroupBox("Alignment")
        self._align_layout = TextAlignLayout(item.alignH(), item.alignV())
        self._align_group_box.setLayout(self._align_layout)
        self._left_layout.addWidget(self._align_group_box)
        # origin section
        self._origin_group_box = QGroupBox("Origin")
        self._origin_layout = OriginLayout(item.origin())
        self._origin_group_box.setLayout(self._origin_layout)
        # done
        self._left_layout.addWidget(self._origin_group_box)
        ########################################################################
        # middle right
        ########################################################################
        self._right_layout = QVBoxLayout()
        # appearance section
        self._appearance_group_box = QGroupBox("Appearance")
        self._appearance_layout = TextAppearancePreviewLayout(
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
        self._appearance_group_box.setLayout(self._appearance_layout)
        self._right_layout.addWidget(self._appearance_group_box)
        ########################################################################
        # middle
        ########################################################################
        self._middle_layout = QHBoxLayout()
        self._middle_layout.addLayout(self._left_layout)
        self._middle_layout.addLayout(self._right_layout)
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
        self._format_layout.onFormatChange()  # initialise value

    def showEvent(self : Self, event : QShowEvent):
        """Override showEvent to select all text when dialog appears."""
        super().showEvent(event)
        QTimer.singleShot(0, lambda: (
            self._value_layout._edit.setFocus(Qt.FocusReason.PopupFocusReason),
            self._value_layout._edit.selectAll()
        ))

    def getText(self : Self) -> str:
        return self._value_layout.getValue()

    def getBlock(self : Self) -> bool:
        return self._format_layout.getBlock()

    def getRotcomp(self : Self) -> bool:
        return self._rotcomp_checkbox.isChecked()

    def getAlignH(self : Self) -> AlignH:
        return self._align_layout.getAlignH()

    def getAlignV(self : Self) -> AlignV:
        return self._align_layout.getAlignV()

    def getOrigin(self : Self) -> str:
        return self._origin_layout.getOrigin()

    def getColor(self : Self) -> QColor | Default | NoChange:
        return self._appearance_layout.getColor()

    def getFamily(self : Self) -> str | Default | NoChange:
        return self._appearance_layout.getFamily()

    def getSize(self : Self) -> float | NoChange | Default:
        return self._appearance_layout.getSize()

    def getBold(self : Self) -> bool | Default | NoChange:
        return self._appearance_layout.getBold()

    def getItalic(self : Self) -> bool | Default | NoChange:
        return self._appearance_layout.getItalic()

    def getUnderline(self : Self) -> bool | Default | NoChange:
        return self._appearance_layout.getUnderline()
