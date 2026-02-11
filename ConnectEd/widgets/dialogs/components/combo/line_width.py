from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget, QComboBox
from PyQt6.QtGui     import QIcon, QPixmap, QPainter, QPen

from .....core.types import Default, DEFAULT, NoChange, NO_CHANGE
from .....core.icon  import getFgBgColors
from .....core.utils import val2str

from .. import CUSTOM_ICON_SIZE, NoChangeIcon, DefaultIcon, QueryIcon

from ...float import FloatDialog


class LineWidthComboBox(QComboBox):
    def __init__(
        self      : Self,
        initial   : float | int | Default | NoChange,
        default   : float | int | NoChange,
        parent    : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        if isinstance(initial, int):
            initial = float(initial)
        if isinstance(default, int):
            default = float(default)
        self.setIconSize(CUSTOM_ICON_SIZE)
        # add no change option if applicable
        if initial is NO_CHANGE:
            self.addItem(NoChangeIcon().get(), "<no change>", NO_CHANGE)
            current_idx = 0
        # add default option
        if initial is DEFAULT:
            current_idx = self.count()
        default_icon = self._getIcon(default) if isinstance(default, float) \
            else DefaultIcon().get()
        default_str = f" = {val2str(default)}" if isinstance(default, float) \
            else ""
        default_value = default if isinstance(default, float) else NO_CHANGE
        self.addItem(default_icon, f"<default{default_str}>", default_value)
        # add custom option
        if isinstance(initial, float):
            current_idx = self.count()
        custom_icon = self._getIcon(initial) if isinstance(initial, float) \
            else default_icon if isinstance(default, float) \
            else QueryIcon().get()
        custom_str = f" = {val2str(initial)}" if isinstance(initial, float) \
            else default_str if isinstance(default, float) \
            else ""
        custom_value = initial if isinstance(initial, float) \
            else default if isinstance(default, float) \
            else None
        self.addItem(custom_icon, f"<custom{custom_str}>", custom_value)
        # add standard widths
        for i in range(1, 4):
            if initial == i:
                current_idx = self.count()
            self.addItem(self._getIcon(i), str(i), float(i))
        # set current index
        self.setCurrentIndex(current_idx)
        self.activated.connect(self._onActivated)

    def getChoice(self : Self) -> NoChange | Default | float | int:
        return self.itemData(self.currentIndex(), Qt.ItemDataRole.UserRole)

    def _onActivated(self : Self, index : int) -> None:
        if self.currentText().startswith("<custom"):
            dialog = FloatDialog(title="Line Width", parent=self)
            if dialog.exec():
                w = dialog.getChoice()
                if w is not None:
                    self.setItemText(index, f"<custom = {val2str(w)}>")
                    self.setItemIcon(index, self._getIcon(w))
                    self.setItemData(index, w, Qt.ItemDataRole.UserRole)

    def _getIcon(self : Self, width : float | int) -> QIcon:
        fg, bg = getFgBgColors()
        size = self.iconSize()
        pixmap = QPixmap(size.width(), size.height())
        pixmap.fill(Qt.GlobalColor.transparent)
        with QPainter(pixmap) as painter:
            painter.fillRect(0, 0, size.width(), size.height(), bg)
            painter.setPen(QPen(fg, width, Qt.PenStyle.SolidLine))
            painter.drawLine(
                0, size.height() // 2, size.width() - 1, size.height() // 2
            )
        return QIcon(pixmap)
