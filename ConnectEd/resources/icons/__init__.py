from PyQt6.QtCore import QSize

from ...core.icon import SvgIconSingleton

from .. import getIconPath


class TextAlignLeftIcon(SvgIconSingleton):
    PATH = getIconPath("text_align_left.svg")
    SIZE = QSize(16, 16)


class TextAlignCenterIcon(SvgIconSingleton):
    PATH = getIconPath("text_align_center.svg")
    SIZE = QSize(16, 16)


class TextAlignRightIcon(SvgIconSingleton):
    PATH = getIconPath("text_align_right.svg")
    SIZE = QSize(16, 16)


class TextAlignTopIcon(SvgIconSingleton):
    PATH = getIconPath("text_align_top.svg")
    SIZE = QSize(16, 16)


class TextAlignMiddleIcon(SvgIconSingleton):
    PATH = getIconPath("text_align_middle.svg")
    SIZE = QSize(16, 16)


class TextAlignBottomIcon(SvgIconSingleton):
    PATH = getIconPath("text_align_bottom.svg")
    SIZE = QSize(16, 16)
