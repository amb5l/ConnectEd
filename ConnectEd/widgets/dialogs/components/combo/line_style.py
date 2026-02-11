from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget, QComboBox
from PyQt6.QtGui     import QIcon, QPixmap, QPainter, QPen

from .....app import logger

from .....core.icon import getFgBgColors

from .....core.types import Default, DEFAULT, NoChange, NO_CHANGE

from .. import CUSTOM_ICON_SIZE, NoChangeIcon, DefaultIcon


class LineStyleComboBox(QComboBox):
    _STYLES = {
        "No Line"      : Qt.PenStyle.NoPen,
        "Solid"        : Qt.PenStyle.SolidLine,
        "Dash"         : Qt.PenStyle.DashLine,
        "Dot"          : Qt.PenStyle.DotLine,
        "Dash Dot"     : Qt.PenStyle.DashDotLine,
        "Dash Dot Dot" : Qt.PenStyle.DashDotDotLine
    }
    _STYLES_REV = {v: k for k, v in _STYLES.items()}

    def __init__(
        self      : Self,
        initial   : Qt.PenStyle | Default | NoChange,
        default   : Qt.PenStyle | NoChange,
        parent    : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setIconSize(CUSTOM_ICON_SIZE)
        # add no change option if applicable
        if initial is NO_CHANGE:
            self.addItem(NoChangeIcon().get(), "<no change>", NO_CHANGE)
            current_idx = 0
        # add default option
        if initial is DEFAULT:
            current_idx = self.count()
        default_icon = self._getIcon(default) \
            if isinstance(default, Qt.PenStyle) else DefaultIcon().get()
        default_str = f" = {self._STYLES_REV[default]}" \
            if isinstance(default, Qt.PenStyle) else ""
        default_value = default if isinstance(default, Qt.PenStyle) else NO_CHANGE
        self.addItem(default_icon, f"<default{default_str}>", default_value)
        # add standard styles
        for k, v in self._STYLES.items():
            if initial == v:
                current_idx = self.count()
            self.addItem(self._getIcon(v), k, v)
        # set current index
        self.setCurrentIndex(current_idx)

    def getChoice(self : Self) -> Qt.PenStyle | Default | NoChange:
        return self.itemData(self.currentIndex(), Qt.ItemDataRole.UserRole)

    def _getIcon(self : Self, style : Qt.PenStyle) -> QIcon:
        fg, bg = getFgBgColors()
        size = self.iconSize()
        pixmap = QPixmap(size.width(), size.height())
        pixmap.fill(Qt.GlobalColor.transparent)
        with QPainter(pixmap) as painter:
            painter.fillRect(0, 0, size.width(), size.height(), bg)
            painter.setPen(QPen(fg, 1, style))
            painter.drawLine(
                0, size.height() // 2, size.width() - 1, size.height() // 2
            )
        return QIcon(pixmap)
