from typing import Self

from PyQt6.QtWidgets import QGridLayout, QVBoxLayout, QHBoxLayout, QGroupBox, \
                            QButtonGroup, QLabel

from ....graphics.items import AlignH, AlignV

from .....resources.icons import TextAlignLeftIcon,   \
                                 TextAlignCenterIcon, \
                                 TextAlignRightIcon,  \
                                 TextAlignTopIcon,    \
                                 TextAlignMiddleIcon, \
                                 TextAlignBottomIcon

from ..tool_button import ToolButton


class TextAlignLayout(QVBoxLayout):
    _group_box       : QGroupBox
    _layout          : QGridLayout
    _h_label         : QLabel
    _h_layout        : QHBoxLayout
    _h_button_group  : QButtonGroup
    _h_left_button   : ToolButton
    _h_center_button : ToolButton
    _h_right_button  : ToolButton
    _v_label         : QLabel
    _v_layout        : QHBoxLayout
    _v_group         : QButtonGroup
    _v_top_button    : ToolButton
    _v_middle_button : ToolButton
    _v_bottom_button : ToolButton

    def __init__(self : Self, align_h : AlignH, align_v : AlignV) -> None:
        super().__init__()
        self._group_box = QGroupBox("Alignment")
        self._layout = QGridLayout()
        # horizontal
        self._h_label = QLabel("Horizontal:")
        self._layout.addWidget(self._h_label, 0, 0)
        self._h_layout = QHBoxLayout()
        self._h_button_group = QButtonGroup(self)
        self._h_left_button = ToolButton(TextAlignLeftIcon().get())
        self._h_left_button.setChecked(align_h == AlignH.LEFT)
        self._h_button_group.addButton(self._h_left_button)
        self._h_layout.addWidget(self._h_left_button)
        self._h_center_button = ToolButton(TextAlignCenterIcon().get())
        self._h_center_button.setChecked(align_h == AlignH.CENTER)
        self._h_button_group.addButton(self._h_center_button)
        self._h_layout.addWidget(self._h_center_button)
        self._h_right_button = ToolButton(TextAlignRightIcon().get())
        self._h_right_button.setChecked(align_h == AlignH.RIGHT)
        self._h_button_group.addButton(self._h_right_button)
        self._h_layout.addWidget(self._h_right_button)
        self._layout.addLayout(self._h_layout, 0, 1)
        # vertical
        self._v_label = QLabel("Vertical:")
        self._layout.addWidget(self._v_label, 1, 0)
        self._v_layout = QHBoxLayout()
        self._v_group = QButtonGroup(self)
        self._v_top_button = ToolButton(TextAlignTopIcon().get())
        self._v_top_button.setChecked(align_v == AlignV.TOP)
        self._v_group.addButton(self._v_top_button)
        self._v_layout.addWidget(self._v_top_button)
        self._v_middle_button = ToolButton(TextAlignMiddleIcon().get())
        self._v_middle_button.setChecked(align_v == AlignV.MIDDLE)
        self._v_group.addButton(self._v_middle_button)
        self._v_layout.addWidget(self._v_middle_button)
        self._v_bottom_button = ToolButton(TextAlignBottomIcon().get())
        self._v_bottom_button.setChecked(align_v == AlignV.BOTTOM)
        self._v_group.addButton(self._v_bottom_button)
        self._v_layout.addWidget(self._v_bottom_button)
        self._layout.addLayout(self._v_layout, 1, 1)
        # complete
        self._group_box.setLayout(self._layout)
        self.addWidget(self._group_box)

    def getAlignH(self : Self) -> AlignH:
        if self._h_left_button.isChecked():
            return AlignH.LEFT
        elif self._h_center_button.isChecked():
            return AlignH.CENTER
        else:
            return AlignH.RIGHT

    def getAlignV(self : Self) -> AlignV:
        if self._v_top_button.isChecked():
            return AlignV.TOP
        elif self._v_middle_button.isChecked():
            return AlignV.MIDDLE
        else:
            return AlignV.BOTTOM
