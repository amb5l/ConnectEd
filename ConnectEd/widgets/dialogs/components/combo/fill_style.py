from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget, QComboBox
from PyQt6.QtGui     import QIcon, QPixmap, QPainter, QBrush

from .....app import logger

from .....core.check import checked
from .....core.types import Default, DEFAULT, NoChange, NO_CHANGE, BrushStyle
from .....core.icon import getFgBgColors

from .. import customIconSize, NoChangeIcon, DefaultIcon


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

    _initial     : BrushStyle | NoChange
    _idx_default : int

    @checked
    def __init__(
        self    : Self,
        value   : BrushStyle | NoChange,
        default : Qt.BrushStyle | Default,
        parent  : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._initial = value
        self.setIconSize(customIconSize())
        # build default icon, string and value
        default_icon = self._getIcon(default) \
            if isinstance(default, Qt.BrushStyle) else DefaultIcon().get()
        default_str = f" = {self._STYLES_REV[default]}" \
            if isinstance(default, Qt.BrushStyle) else ""
        # build no change icon, string and value
        no_change_icon = self._getIcon(value) if isinstance(value, Qt.BrushStyle) \
            else default_icon if value == DEFAULT \
            else NoChangeIcon().get()
        no_change_str = f" = {self._STYLES_REV[value]}" \
            if isinstance(value, Qt.BrushStyle) else ""
        no_change_value = value if isinstance(value, Qt.BrushStyle) \
            else DEFAULT if value == DEFAULT \
            else NO_CHANGE
        # add no change and default entries
        if value is NO_CHANGE:
            self.addItem(no_change_icon, f"<no change{no_change_str}>", no_change_value)
        self._idx_default = self.count()
        self.addItem(default_icon, f"<default{default_str}>", DEFAULT)
        # add standard entries, set current index
        self.setCurrentIndex(0)
        if value is not NO_CHANGE and value != DEFAULT:
            self.setCurrentIndex(1)
        for k, v in self._STYLES.items():
            self.addItem(self._getIcon(v), k, v)
            if value == v:
                self.setCurrentIndex(self.count() - 1)

    @checked
    def value(self : Self) -> BrushStyle | NoChange:
        r = self.itemData(self.currentIndex(), Qt.ItemDataRole.UserRole)
        return r if r != self._initial else NO_CHANGE

    @checked
    def setValue(self : Self, value : BrushStyle) -> None:
        if value == DEFAULT:
            index = self._idx_default
        else:
            index = self.findData(value, Qt.ItemDataRole.UserRole)
            if index < 0:
                logger().error(f"Invalid value: {value}")
                return
        self.setCurrentIndex(index)

    @checked
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
