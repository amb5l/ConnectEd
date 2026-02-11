from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget, QComboBox
from PyQt6.QtGui     import QColor, QIcon, QPixmap, QPainter

from .....core.utils import val2str

from .....core.types import Default, DEFAULT, NoChange, NO_CHANGE

from .. import CUSTOM_ICON_SIZE, NoChangeIcon, DefaultIcon, QueryIcon

from ..dialog import CustomColorDialog


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

    _choice  : QColor | Default | NoChange

    def __init__(
        self    : Self,
        initial : QColor | Default | NoChange,
        default : QColor | NoChange,
        parent  : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setIconSize(CUSTOM_ICON_SIZE)
        # add no change option if applicable
        if initial is NO_CHANGE:
            self.addItem(NoChangeIcon().get(), "<no change>")
            current_idx = 0
        # add default option
        if initial is DEFAULT:
            current_idx = self.count()
        default_icon = self._getIcon(default) if isinstance(default, QColor) \
            else DefaultIcon().get()
        default_str = f" = {val2str(default)}" if isinstance(default, QColor) \
            else ""
        self.addItem(default_icon, f"<default{default_str}>")
        # add custom option
        if isinstance(initial, QColor):
            current_idx = self.count()
        custom_icon = self._getIcon(initial) if isinstance(initial, QColor) \
            else default_icon if isinstance(default, QColor) \
            else QueryIcon().get()
        custom_str = f" = {val2str(initial)}" if isinstance(initial, QColor) \
            else default_str if isinstance(default, QColor) \
            else ""
        self.addItem(custom_icon, f"<custom{custom_str}>")
        # add standard colors
        for k, v in self._COLORS.items():
            if initial == v:
                current_idx = self.count()
            self.addItem(self._getIcon(v), k)
        # set current index
        self.setCurrentIndex(current_idx)
        self._choice = initial
        self.activated.connect(self._onActivated)

    def getChoice(self : Self) -> QColor | Default | NoChange:
        return self._choice

    def _onActivated(self : Self, index : int) -> None:
        selected_text = self.currentText()
        if selected_text.startswith("<no change"):
            self._choice = NO_CHANGE
        elif selected_text.startswith("<default"):
            self._choice = DEFAULT
        elif selected_text.startswith("<custom"):
            dialog = CustomColorDialog(
                self._choice if isinstance(self._choice, QColor) else None,
                parent=self
            )
            if dialog.exec():
                self._choice = dialog.getChoice()
                self.setItemIcon(index, self._getIcon(self._choice))
                self.setItemText(index, f"<custom = {val2str(self._choice)}>")
        else:
            self._choice = self._COLORS[selected_text]

    def _getIcon(self : Self, color : QColor) -> QIcon:
        size = self.iconSize()
        pixmap = QPixmap(size.width(), size.height())
        pixmap.fill(color)
        with QPainter(pixmap) as painter:
            painter.fillRect(0, 0, size.width(), size.height(), color)
        return QIcon(pixmap)
