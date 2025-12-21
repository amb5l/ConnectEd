from PyQt6.QtCore import QSize

from ...core.icon import SvgIconSingleton

from .. import getIconPath


class SvgIcon16x16(SvgIconSingleton):
    SIZE = QSize(16, 16)


class AnchorTopLeftIcon(SvgIcon16x16):
    PATH = getIconPath("anchor_top_left.svg")


class AnchorTopCenterIcon(SvgIcon16x16):
    PATH = getIconPath("anchor_top_center.svg")


class AnchorTopRightIcon(SvgIcon16x16):
    PATH = getIconPath("anchor_top_right.svg")


class AnchorMiddleLeftIcon(SvgIcon16x16):
    PATH = getIconPath("anchor_middle_left.svg")


class AnchorMiddleCenterIcon(SvgIcon16x16):
    PATH = getIconPath("anchor_middle_center.svg")


class AnchorMiddleRightIcon(SvgIcon16x16):
    PATH = getIconPath("anchor_middle_right.svg")


class AnchorBottomLeftIcon(SvgIcon16x16):
    PATH = getIconPath("anchor_bottom_left.svg")


class AnchorBottomCenterIcon(SvgIcon16x16):
    PATH = getIconPath("anchor_bottom_center.svg")


class AnchorBottomRightIcon(SvgIcon16x16):
    PATH = getIconPath("anchor_bottom_right.svg")


class TextAlignLeftIcon(SvgIcon16x16):
    PATH = getIconPath("text_align_left.svg")


class TextAlignCenterIcon(SvgIcon16x16):
    PATH = getIconPath("text_align_center.svg")


class TextAlignRightIcon(SvgIcon16x16):
    PATH = getIconPath("text_align_right.svg")


class TextAlignTopIcon(SvgIcon16x16):
    PATH = getIconPath("text_align_top.svg")


class TextAlignMiddleIcon(SvgIcon16x16):
    PATH = getIconPath("text_align_middle.svg")


class TextAlignBottomIcon(SvgIcon16x16):
    PATH = getIconPath("text_align_bottom.svg")
