from PyQt6.QtCore import QSize

from ....core.check import checked
from ....core.icon import getDefaultIconSize, SvgIconSingleton

from ....resources import getIconPath


_custom_icon_size : QSize | None = None

@checked
def customIconSize() -> QSize:
    global _custom_icon_size
    if _custom_icon_size is None:
        s = getDefaultIconSize()
        _custom_icon_size = QSize(s * 2, s)
    return _custom_icon_size


class BaseIcon(SvgIconSingleton):
    SIZE = customIconSize()

class NoChangeIcon(BaseIcon):
    PATH = getIconPath("no_change.svg")

    @property
    def SIZE(self) -> QSize:
        return customIconSize()


class DefaultIcon(BaseIcon):
    PATH = getIconPath("default.svg")

    @property
    def SIZE(self) -> QSize:
        return customIconSize()


class QueryIcon(BaseIcon):
    FONT_FAMILY = "Arial"
    CHAR = "?"

    @property
    def SIZE(self) -> QSize:
        return customIconSize()
