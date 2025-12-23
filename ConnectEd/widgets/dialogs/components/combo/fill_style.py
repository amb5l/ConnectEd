from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget, QComboBox
from PyQt6.QtGui     import QIcon, QPixmap, QPainter, QBrush

from .....app import logger

from .....core.icon import getFgBgColors

from ....graphics.items import NoChange, Default, DEFAULT, NO_CHANGE

from .. import CUSTOM_ICON_SIZE, NoChangeIcon, DefaultIcon


class FillStyleComboBox(QComboBox):
    STYLES = {
        "<no change>" : NO_CHANGE,
        "<default>"   : DEFAULT,
        "No Fill"     : Qt.BrushStyle.NoBrush,
        "Solid"       : Qt.BrushStyle.SolidPattern,
        "Dense1"      : Qt.BrushStyle.Dense1Pattern,
        "Dense2"      : Qt.BrushStyle.Dense2Pattern,
        "Dense3"      : Qt.BrushStyle.Dense3Pattern,
        "Dense4"      : Qt.BrushStyle.Dense4Pattern,
        "Dense5"      : Qt.BrushStyle.Dense5Pattern,
        "Dense6"      : Qt.BrushStyle.Dense6Pattern,
        "Dense7"      : Qt.BrushStyle.Dense7Pattern,
        "Hor"         : Qt.BrushStyle.HorPattern,
        "Ver"         : Qt.BrushStyle.VerPattern,
        "Cross"       : Qt.BrushStyle.CrossPattern,
        "BDiag"       : Qt.BrushStyle.BDiagPattern,
        "FDiag"       : Qt.BrushStyle.FDiagPattern,
        "DiagCross"   : Qt.BrushStyle.DiagCrossPattern
    }
    STYLES_REVERSE = {v: k for k, v in STYLES.items()}

    def __init__(
        self      : Self,
        initial   : Qt.BrushStyle | Default | NoChange,
        default   : Qt.BrushStyle | Default,
        parent    : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setIconSize(CUSTOM_ICON_SIZE)
        if isinstance(default, Qt.BrushStyle):
            default_icon = self.getIcon(default)
            default_str = f" = {self.STYLES_REVERSE[default]}"
        else:
            default_icon = DefaultIcon().get()
            default_str = ""
        if isinstance(initial, Qt.BrushStyle):
            no_change_icon = self.getIcon(initial)
            no_change_str = f" = {self.STYLES_REVERSE[initial]}"
        elif initial is DEFAULT:
            no_change_icon = default_icon
            no_change_str = f" = default{default_str}"
        for i, (k, v) in enumerate(self.STYLES.items()):
            match k:
                case "<no change>":
                    icon = no_change_icon
                    text = f"<no change{no_change_str}>"
                case "<default>":
                    icon = default_icon
                    text = f"<default{default_str}>"
                case _:
                    icon = self.getIcon(v)
                    text = f"{self.STYLES_REVERSE[v]}"
            self.addItem(icon, text, v)
            if initial == v:
                self.setCurrentIndex(i)

    def getIcon(self : Self, style : Qt.BrushStyle) -> QIcon:
        fg, bg = getFgBgColors()
        size = self.iconSize()
        pixmap = QPixmap(size.width(), size.height())
        pixmap.fill(Qt.GlobalColor.transparent)
        with QPainter(pixmap) as painter:  # Use context manager for painter
            painter.fillRect(0, 0, size.width(), size.height(), bg)
            painter.setBrush(QBrush(fg, style))
            painter.drawRect(0, 0, size.width(), size.height())
        return QIcon(pixmap)

    def getChoice(self : Self) -> Qt.BrushStyle | Default | NoChange:
        text = self.currentText()
        if text.startswith("<no change"):
            return NO_CHANGE
        elif text.startswith("<default"):
            return DEFAULT
        else:
            keys = list(self.STYLES.keys())
            if text in keys:
                return self.STYLES[text]
            logger().warning(f"Invalid fill style: {text}")
            return Qt.BrushStyle.NoBrush
