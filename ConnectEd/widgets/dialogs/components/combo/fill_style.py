from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget, QComboBox
from PyQt6.QtGui     import QIcon, QPixmap, QPainter, QBrush

from .....app import logger

from .....core.icon import getFgBgColors

from .....core.types import Default, DEFAULT, NoChange, NO_CHANGE

from .. import CUSTOM_ICON_SIZE, NoChangeIcon, DefaultIcon, QueryIcon


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
        # build default icon, string and value
        default_icon = self._getIcon(default) \
            if isinstance(default, Qt.BrushStyle) else DefaultIcon().get()
        default_str = f" = {self._STYLES_REV[default]}" \
            if isinstance(default, Qt.BrushStyle) else ""
        default_value = default if isinstance(default, Qt.BrushStyle) else NO_CHANGE
        # build no change icon, string and value
        no_change_icon = self._getIcon(initial) if isinstance(initial, Qt.BrushStyle) \
            else default_icon if initial is DEFAULT \
            else NoChangeIcon().get()
        no_change_str = f" = {self._STYLES_REV[initial]}" \
            if isinstance(initial, Qt.BrushStyle) else ""
        no_change_value = initial if isinstance(initial, Qt.BrushStyle) \
            else default_value if initial is DEFAULT \
            else NO_CHANGE
        # add no change and default entries
        if initial is NO_CHANGE:
            self.addItem(no_change_icon, f"<no change{no_change_str}>", no_change_value)
        self.addItem(default_icon, f"<default{default_str}>", default_value)
        # add standard entries, set current index
        self.setCurrentIndex(0)
        if initial is not NO_CHANGE and initial is not DEFAULT:
            self.setCurrentIndex(1)
        for k, v in self._STYLES.items():
            self.addItem(self._getIcon(v), k, v)
            if initial == v:
                self.setCurrentIndex(self.count() - 1)

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
