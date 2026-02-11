from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget, QComboBox
from PyQt6.QtGui     import QIcon, QPixmap, QPainter, QPen

from .....app import logger

from .....core.icon import getFgBgColors

from .....core.types import Default, DEFAULT, NoChange, NO_CHANGE

from .. import CUSTOM_ICON_SIZE, NoChangeIcon, DefaultIcon


class LineStyleComboBox(QComboBox):
    STYLES = {
        "<no change>"    : NO_CHANGE,
        "<default>"      : DEFAULT,
        "No Line"      : Qt.PenStyle.NoPen,
        "Solid"        : Qt.PenStyle.SolidLine,
        "Dash"         : Qt.PenStyle.DashLine,
        "Dot"          : Qt.PenStyle.DotLine,
        "Dash Dot"     : Qt.PenStyle.DashDotLine,
        "Dash Dot Dot" : Qt.PenStyle.DashDotDotLine
    }
    STYLES_REVERSE = {v: k for k, v in STYLES.items()}

    def __init__(
        self      : Self,
        initial   : NoChange | Default | Qt.PenStyle,
        default   : Default | Qt.PenStyle,
        parent    : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setIconSize(CUSTOM_ICON_SIZE)
        # Determine default icon and string
        if isinstance(default, Qt.PenStyle):
            default_icon = self.getIcon(default)
            default_str = f" = {self.STYLES_REVERSE[default]}"
        else:
            default_icon = DefaultIcon().get()
            default_str = ""
        # Determine no_change icon and string from initial
        if isinstance(initial, Qt.PenStyle):
            no_change_icon = self.getIcon(initial)
            no_change_str = f" = {self.STYLES_REVERSE[initial]}"
        elif initial is DEFAULT:
            no_change_icon = default_icon
            no_change_str = f" = default{default_str}"
        else:  # NO_CHANGE
            no_change_icon = NoChangeIcon().get()
            no_change_str = ""
        idx = 0
        for k, v in self.STYLES.items():
            match k:
                case "<no change>":
                    icon = no_change_icon
                    text = f"<no change{no_change_str}>"
                case "<default>":
                    icon = default_icon
                    text = f"<default{default_str}>"
                case _:
                    icon = self.getIcon(v)
                    text = k
            self.addItem(icon, text)
            if initial == v:
                self.setCurrentIndex(idx)
            idx += 1

    def getIcon(self : Self, style : Qt.PenStyle) -> QIcon:
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

    def getChoice(self : Self) -> Qt.PenStyle | Default | NoChange:
        text = self.currentText()
        if text.startswith("<no change"):
            return NO_CHANGE
        elif text.startswith("<default"):
            return DEFAULT
        else:
            keys = list(self.STYLES.keys())
            if text in keys:
                return self.STYLES[text]
            logger().warning(f"Invalid line style: {text}")
            return Qt.PenStyle.SolidLine
