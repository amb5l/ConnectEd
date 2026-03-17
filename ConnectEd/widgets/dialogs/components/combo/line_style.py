from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget, QComboBox
from PyQt6.QtGui     import QIcon, QPixmap, QPainter, QPen

from .....app import logger

from .....core.check import checked
from .....core.icon  import getFgBgColors

from .....core.types import Default, DEFAULT, NoChange, NO_CHANGE

from .. import customIconSize, NoChangeIcon, DefaultIcon


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

    _idx_default : int

    @checked
    def __init__(
        self    : Self,
        value   : Qt.PenStyle | Default | NoChange,
        default : Qt.PenStyle | NoChange,
        parent  : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setIconSize(customIconSize())
        # build default icon, string and value
        default_icon = self._getIcon(default) \
            if isinstance(default, Qt.PenStyle) else DefaultIcon().get()
        default_str = f" = {self._STYLES_REV[default]}" \
            if isinstance(default, Qt.PenStyle) else ""
        default_value = default if isinstance(default, Qt.PenStyle) else NO_CHANGE
        # build no change icon, string and value
        no_change_icon = self._getIcon(value) if isinstance(value, Qt.PenStyle) \
            else default_icon if value is DEFAULT \
            else NoChangeIcon().get()
        no_change_str = f" = {self._STYLES_REV[value]}" \
            if isinstance(value, Qt.PenStyle) else ""
        no_change_value = value if isinstance(value, Qt.PenStyle) \
            else default_value if value is DEFAULT \
            else NO_CHANGE
        # add no change and default entries
        if value is NO_CHANGE:
            self.addItem(no_change_icon, f"<no change{no_change_str}>", no_change_value)
        self._idx_default = self.count()
        self.addItem(default_icon, f"<default{default_str}>", default_value)
        # add standard entries, set current index
        self.setCurrentIndex(0)
        if value is not NO_CHANGE and value is not DEFAULT:
            self.setCurrentIndex(1)
        for k, v in self._STYLES.items():
            self.addItem(self._getIcon(v), k, v)
            if value == v:
                self.setCurrentIndex(self.count() - 1)

    @checked
    def value(self : Self) -> Qt.PenStyle | Default | NoChange:
        return self.itemData(self.currentIndex(), Qt.ItemDataRole.UserRole)

    @checked
    def setValue(self : Self, value : Qt.PenStyle | Default) -> None:
        if value is DEFAULT:
            index = self._idx_default
        else:
            index = self.findData(value, Qt.ItemDataRole.UserRole)
            if index < 0:
                logger().error(f"Invalid value: {value}")
                return
        self.setCurrentIndex(index)

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
