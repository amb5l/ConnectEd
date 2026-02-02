from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget, QComboBox
from PyQt6.QtGui     import QColor, QIcon, QPixmap, QPainter

from .....core.utils import val2str

from ....graphics.items import NoChange, Default, DEFAULT, NO_CHANGE

from .. import CUSTOM_ICON_SIZE, NoChangeIcon, DefaultIcon, QueryIcon

from ..dialog import CustomColorDialog


class ColorComboBox(QComboBox):
    _COLORS = {
        "<no change>"  : NO_CHANGE,
        "<default>"    : DEFAULT,
        "<custom>"     : "placeholder",
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

    _choice : NoChange | Default | QColor

    def __init__(
        self      : Self,
        initial   : NoChange | Default | QColor,
        default   : Default | QColor,
        parent    : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setIconSize(CUSTOM_ICON_SIZE)
        # Determine default icon and string
        if isinstance(default, QColor):
            default_icon = self.getIcon(default)
            default_str = f" = {val2str(default)}"
        else:
            default_icon = DefaultIcon().get()
            default_str = ""
        # Determine no_change icon and string from initial
        if isinstance(initial, QColor):
            no_change_icon = self.getIcon(initial)
            no_change_str = f" = {val2str(initial)}"
        elif initial is DEFAULT:
            no_change_icon = default_icon
            no_change_str = f" = default{default_str}"
        else:  # NO_CHANGE
            no_change_icon = NoChangeIcon().get()
            no_change_str = ""
        custom = True
        custom_idx = None
        for k, v in self._COLORS.items():
            i = self.count()
            match k:
                case "<no change>":
                    icon = no_change_icon
                    text = f"<no change{no_change_str}>"
                case "<default>":
                    icon = default_icon
                    text = f"<default{default_str}>"
                case "<custom>":
                    custom_idx = i
                    icon = QueryIcon().get()
                    text = k
                case _:
                    icon = self.getIcon(v)
                    text = k
            self.addItem(icon, text)
            if initial == v:
                self.setCurrentIndex(i)
                custom = False
            elif initial is NO_CHANGE and k == "<no change>":
                self.setCurrentIndex(i)
                custom = False
            elif isinstance(initial, Default) and k == "<default>":
                self.setCurrentIndex(i)
                custom = False
        if isinstance(initial, QColor) and custom and custom_idx is not None:
            self.setCurrentIndex(custom_idx)
            self.setItemIcon(custom_idx, self.getIcon(initial))
            self.setItemText(custom_idx, f"<custom = {val2str(initial)}>")
        self._choice = initial
        self.activated.connect(self.onActivated)

    def onActivated(self : Self, index : int) -> None:
        selected_text = self.currentText()
        if selected_text == "<no change>":
            self._choice = NO_CHANGE
        elif selected_text == "<default>":
            self._choice = DEFAULT
        elif selected_text.startswith("<custom"):
            dialog = CustomColorDialog(
                self._choice if isinstance(self._choice, QColor) else None,
                parent=self
            )
            if dialog.exec():
                self._choice = dialog.getChoice()
                self.setItemIcon(index, self.getIcon(self._choice))
                self.setItemText(index, f"<custom = {val2str(self._choice)}>")
        else:
            self._choice = self._COLORS[selected_text]

    def getIcon(self : Self, color : QColor) -> QIcon:
        size = self.iconSize()
        pixmap = QPixmap(size.width(), size.height())
        pixmap.fill(color)
        with QPainter(pixmap) as painter:
            painter.fillRect(0, 0, size.width(), size.height(), color)
        return QIcon(pixmap)

    def getChoice(self : Self) -> QColor | Default | NoChange:
        return self._choice
