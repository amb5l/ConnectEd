from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget, QComboBox
from PyQt6.QtGui     import QColor, QIcon, QPixmap, QPainter

from .....app import logger

from .....core.check import checked
from .....core.types import Default, DEFAULT, NoChange, NO_CHANGE
from .....core.utils import val2str

from .. import CUSTOM_ICON_SIZE, NoChangeIcon, DefaultIcon, QueryIcon

from ...color import ColorDialog


class ColorComboBox(QComboBox):
    _COLORS = {
        "Black"        : QColor(Qt.GlobalColor.black),
        "Dark Red"     : QColor(Qt.GlobalColor.darkRed),
        "Red"          : QColor(Qt.GlobalColor.red),
        "Dark Yellow"  : QColor(Qt.GlobalColor.darkYellow),
        "Yellow"       : QColor(Qt.GlobalColor.yellow),
        "Dark Green"   : QColor(Qt.GlobalColor.darkGreen),
        "Green"        : QColor(Qt.GlobalColor.green),
        "Dark Cyan"    : QColor(Qt.GlobalColor.darkCyan),
        "Cyan"         : QColor(Qt.GlobalColor.cyan),
        "Dark Blue"    : QColor(Qt.GlobalColor.darkBlue),
        "Blue"         : QColor(Qt.GlobalColor.blue),
        "Dark Magenta" : QColor(Qt.GlobalColor.darkMagenta),
        "Magenta"      : QColor(Qt.GlobalColor.magenta),
        "Dark Gray"    : QColor(Qt.GlobalColor.darkGray),
        "Gray"         : QColor(Qt.GlobalColor.gray),
        "Light Gray"   : QColor(Qt.GlobalColor.lightGray),
        "White"        : QColor(Qt.GlobalColor.white)
    }

    _idx_default : int
    _idx_custom  : int

    @checked
    def __init__(
        self    : Self,
        initial : QColor | Default | NoChange,
        default : QColor | NoChange,
        parent  : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setIconSize(CUSTOM_ICON_SIZE)
        # build default icon, string and value
        default_icon = self._getIcon(default) if isinstance(default, QColor) \
            else DefaultIcon().get()
        default_str = f" = {val2str(default)}" if isinstance(default, QColor) \
            else ""
        default_value = default if isinstance(default, QColor) else NO_CHANGE
        # build no change icon, string and value
        no_change_icon = self._getIcon(initial) if isinstance(initial, QColor) \
            else default_icon if initial is DEFAULT \
            else NoChangeIcon().get()
        no_change_str = f" = {val2str(initial)}" if isinstance(initial, QColor) \
            else " = default" if initial is DEFAULT \
            else ""
        no_change_value = initial if isinstance(initial, QColor) \
            else default_value if initial is DEFAULT \
            else NO_CHANGE
        # build custom icon, string and value
        custom_icon = no_change_icon if isinstance(initial, QColor) \
            else default_icon if initial is DEFAULT and isinstance(default, QColor) \
            else QueryIcon().get()
        custom_str = no_change_str if isinstance(initial, QColor) \
            else default_str if initial is DEFAULT and isinstance(default, QColor) \
            else ""
        custom_value = initial if isinstance(initial, QColor) \
            else default_value if initial is DEFAULT and isinstance(default, QColor) \
            else None
        # add no change, default and custom entries
        if initial is NO_CHANGE:
            self.addItem(no_change_icon, f"<no change{no_change_str}>", no_change_value)
        self._idx_default = self.count()
        self.addItem(default_icon, f"<default{default_str}>", default_value)
        self._idx_custom = self.count()
        self.addItem(custom_icon, f"<custom{custom_str}>", custom_value)
        # add standard entries, set current index
        self.setCurrentIndex(0)
        if initial is not NO_CHANGE and initial is not DEFAULT:
            self.setCurrentIndex(1)
        for k, v in self._COLORS.items():
            self.addItem(self._getIcon(v), k, v)
            if initial == v:
                self.setItemText(self._idx_custom, f"<custom = {k}>")
                self.setCurrentIndex(self.count() - 1)
            if default == v:
                self.setItemText(self._idx_default, f"<default = {k}>")
        # enable custom dialog
        self.activated.connect(self._onActivated)

    @checked
    def value(self : Self) -> QColor | Default | NoChange:
        return self.itemData(self.currentIndex(), Qt.ItemDataRole.UserRole)

    @checked
    def setValue(self : Self, value : QColor | Default) -> None:
        if value is DEFAULT:
            index = self._idx_default
        else:
            index = self.findData(value, Qt.ItemDataRole.UserRole)
            if index < 0:
                index = self._idx_custom
                self.setItemText(index, f"<custom = {val2str(value)}>")
                self.setItemData(index, value, Qt.ItemDataRole.UserRole)
        self.setCurrentIndex(index)

    def _onActivated(self : Self, index : int) -> None:
        if self.currentText().startswith("<custom"):
            color = self.value()
            dialog = ColorDialog(
                color if isinstance(color, QColor) else None,
                parent=self
            )
            if dialog.exec():
                color = dialog.value()
                self.setItemIcon(index, self._getIcon(color))
                self.setItemText(index, f"<custom = {val2str(color)}>")
                self.setItemData(index, color, Qt.ItemDataRole.UserRole)

    def _getIcon(self : Self, color : QColor) -> QIcon:
        size = self.iconSize()
        pixmap = QPixmap(size.width(), size.height())
        pixmap.fill(color)
        with QPainter(pixmap) as painter:
            painter.fillRect(0, 0, size.width(), size.height(), color)
        return QIcon(pixmap)
