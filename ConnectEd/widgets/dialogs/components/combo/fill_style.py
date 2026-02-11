from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget, QComboBox
from PyQt6.QtGui     import QIcon, QPixmap, QPainter, QBrush

from .....app import logger

from .....core.icon import getFgBgColors

from .....core.types import Default, DEFAULT, NoChange, NO_CHANGE

from .. import CUSTOM_ICON_SIZE, NoChangeIcon, DefaultIcon


class FillStyleComboBox(QComboBox):
    _STYLES = {
        "No Fill"   : Qt.BrushStyle.NoBrush,
        "Solid"     : Qt.BrushStyle.SolidPattern,
        "Dense1"    : Qt.BrushStyle.Dense1Pattern,
        "Dense2"    : Qt.BrushStyle.Dense2Pattern,
        "Dense3"    : Qt.BrushStyle.Dense3Pattern,
        "Dense4"    : Qt.BrushStyle.Dense4Pattern,
        "Dense5"    : Qt.BrushStyle.Dense5Pattern,
        "Dense6"    : Qt.BrushStyle.Dense6Pattern,
        "Dense7"    : Qt.BrushStyle.Dense7Pattern,
        "Hor"       : Qt.BrushStyle.HorPattern,
        "Ver"       : Qt.BrushStyle.VerPattern,
        "Cross"     : Qt.BrushStyle.CrossPattern,
        "BDiag"     : Qt.BrushStyle.BDiagPattern,
        "FDiag"     : Qt.BrushStyle.FDiagPattern,
        "DiagCross" : Qt.BrushStyle.DiagCrossPattern
    }
    _STYLES_REV = {v: k for k, v in _STYLES.items()}

    def __init__(
        self      : Self,
        initial   : Qt.BrushStyle | Default | NoChange,
        default   : Qt.BrushStyle | Default,
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
            if isinstance(default, Qt.BrushStyle) else DefaultIcon().get()
        default_str = f" = {self._STYLES_REV[default]}" \
            if isinstance(default, Qt.BrushStyle) else ""
        default_value = default if isinstance(default, Qt.BrushStyle) else NO_CHANGE
        self.addItem(default_icon, f"<default{default_str}>", default_value)
        # add standard styles
        for k, v in self._STYLES.items():
            if initial == v:
                current_idx = self.count()
            self.addItem(self._getIcon(v), k, v)
        # set current index
        self.setCurrentIndex(current_idx)

    def getChoice(self : Self) -> Qt.BrushStyle | Default | NoChange:
        text = self.currentText()
        if text.startswith("<no change"):
            return NO_CHANGE
        elif text.startswith("<default"):
            return DEFAULT
        else:
            keys = list(self._STYLES.keys())
            if text in keys:
                return self._STYLES[text]
            logger().warning(f"Invalid fill style: {text}")
            return Qt.BrushStyle.NoBrush

    def _getIcon(self : Self, style : Qt.BrushStyle) -> QIcon:
        fg, bg = getFgBgColors()
        size = self.iconSize()
        pixmap = QPixmap(size.width(), size.height())
        pixmap.fill(Qt.GlobalColor.transparent)
        with QPainter(pixmap) as painter:
            painter.fillRect(0, 0, size.width(), size.height(), bg)
            painter.setBrush(QBrush(fg, style))
            painter.drawRect(0, 0, size.width(), size.height())
        return QIcon(pixmap)
