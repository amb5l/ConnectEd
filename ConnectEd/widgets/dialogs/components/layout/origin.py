from typing import Self

from PyQt6.QtWidgets import QGridLayout, QButtonGroup

from .....core.types import RectHandleId

from ..tool_button import ToolButton

from .....resources.icons import AnchorTopLeftIcon,   \
                                 AnchorTopCenterIcon, \
                                 AnchorTopRightIcon,  \
                                 AnchorMiddleLeftIcon, \
                                 AnchorMiddleCenterIcon, \
                                 AnchorMiddleRightIcon, \
                                 AnchorBottomLeftIcon, \
                                 AnchorBottomCenterIcon, \
                                 AnchorBottomRightIcon


class OriginLayout(QGridLayout):
    _button_group         : QButtonGroup
    _top_left_button      : ToolButton
    _top_center_button    : ToolButton
    _top_right_button     : ToolButton
    _middle_left_button   : ToolButton
    _middle_center_button : ToolButton
    _middle_right_button  : ToolButton
    _bottom_left_button   : ToolButton
    _bottom_center_button : ToolButton
    _bottom_right_button  : ToolButton

    def __init__(self : Self, origin : str) -> None:
        super().__init__()
        self._button_group = QButtonGroup(self)
        self._top_left_button = ToolButton(AnchorTopLeftIcon().get())
        self._top_left_button.setChecked(origin == "Top Left")
        self._button_group.addButton(self._top_left_button)
        self.addWidget(self._top_left_button, 0, 0)
        self._top_center_button = ToolButton(AnchorTopCenterIcon().get())
        self._top_center_button.setChecked(origin == "Top Center")
        self._button_group.addButton(self._top_center_button)
        self.addWidget(self._top_center_button, 0, 1)
        self._top_right_button = ToolButton(AnchorTopRightIcon().get())
        self._top_right_button.setChecked(origin == "Top Right")
        self._button_group.addButton(self._top_right_button)
        self.addWidget(self._top_right_button, 0, 2)
        self._middle_left_button = ToolButton(AnchorMiddleLeftIcon().get())
        self._middle_left_button.setChecked(origin == "Middle Left")
        self._button_group.addButton(self._middle_left_button)
        self.addWidget(self._middle_left_button, 1, 0)
        self._middle_center_button = ToolButton(AnchorMiddleCenterIcon().get())
        self._middle_center_button.setChecked(origin == "Middle Center")
        self._button_group.addButton(self._middle_center_button)
        self.addWidget(self._middle_center_button, 1, 1)
        self._middle_right_button = ToolButton(AnchorMiddleRightIcon().get())
        self._middle_right_button.setChecked(origin == "Middle Right")
        self._button_group.addButton(self._middle_right_button)
        self.addWidget(self._middle_right_button, 1, 2)
        self._bottom_left_button = ToolButton(AnchorBottomLeftIcon().get())
        self._bottom_left_button.setChecked(origin == "Bottom Left")
        self._button_group.addButton(self._bottom_left_button)
        self.addWidget(self._bottom_left_button, 2, 0)
        self._bottom_center_button = ToolButton(AnchorBottomCenterIcon().get())
        self._bottom_center_button.setChecked(origin == "Bottom Center")
        self._button_group.addButton(self._bottom_center_button)
        self.addWidget(self._bottom_center_button, 2, 1)
        self._bottom_right_button = ToolButton(AnchorBottomRightIcon().get())
        self._bottom_right_button.setChecked(origin == "Bottom Right")
        self._button_group.addButton(self._bottom_right_button)
        self.addWidget(self._bottom_right_button, 2, 2)

    def getOrigin(self : Self) -> RectHandleId:
        if self._top_left_button.isChecked():
            return RectHandleId.TOP_LEFT
        elif self._top_center_button.isChecked():
            return RectHandleId.TOP_CENTER
        elif self._top_right_button.isChecked():
            return RectHandleId.TOP_RIGHT
        elif self._middle_left_button.isChecked():
            return RectHandleId.MIDDLE_LEFT
        elif self._middle_center_button.isChecked():
            return RectHandleId.MIDDLE_CENTER
        elif self._middle_right_button.isChecked():
            return RectHandleId.MIDDLE_RIGHT
        elif self._bottom_left_button.isChecked():
            return RectHandleId.BOTTOM_LEFT
        elif self._bottom_center_button.isChecked():
            return RectHandleId.BOTTOM_CENTER
        else: # self._bottom_right_button.isChecked()
            return RectHandleId.BOTTOM_RIGHT
        raise ValueError("Invalid origin")
