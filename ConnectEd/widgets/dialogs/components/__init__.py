from PyQt6.QtCore import QSize

from ....core.icon import getDefaultIconSize, SvgIconSingleton, CharIconSingleton

from ....resources import getIconPath


CUSTOM_ICON_SIZE = QSize(getDefaultIconSize() * 2, getDefaultIconSize())


class NoChangeIcon(SvgIconSingleton):
    PATH = getIconPath("no_change.svg")
    SIZE = CUSTOM_ICON_SIZE


class DefaultIcon(SvgIconSingleton):
    PATH = getIconPath("default.svg")
    SIZE = CUSTOM_ICON_SIZE


class QueryIcon(CharIconSingleton):
    FONT_FAMILY = "Arial"
    CHAR = "?"
    SIZE = CUSTOM_ICON_SIZE
