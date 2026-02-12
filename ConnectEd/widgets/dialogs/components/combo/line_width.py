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
        # build default icon, string and value
        default_icon = self._getIcon(default) if isinstance(default, float) \
            else DefaultIcon().get()
        default_str = f" = {val2str(default)}" if isinstance(default, float) \
            else ""
        default_value = default if isinstance(default, float) else NO_CHANGE
        # build no change icon, string and value
        no_change_icon = self._getIcon(initial) if isinstance(initial, float) \
            else default_icon if initial is DEFAULT \
            else NoChangeIcon().get()
        no_change_str = f" = {val2str(initial)}" if isinstance(initial, float) \
            else " = default" if initial is DEFAULT \
            else ""
        no_change_value = initial if isinstance(initial, float) \
            else default_value if initial is DEFAULT \
            else NO_CHANGE
        # build custom icon, string and value
        custom_icon = no_change_icon if isinstance(initial, float) \
            else default_icon if initial is DEFAULT and isinstance(default, float) \
            else QueryIcon().get()
        custom_str = no_change_str if isinstance(initial, float) \
            else default_str if initial is DEFAULT and isinstance(default, float) \
            else ""
        custom_value = initial if isinstance(initial, float) \
            else default_value if initial is DEFAULT and isinstance(default, float) \
            else None
        # add no change, default and custom entries
        if initial is NO_CHANGE:
            self.addItem(no_change_icon, f"<no change{no_change_str}>", no_change_value)
        self.addItem(default_icon, f"<default{default_str}>", default_value)
        self.addItem(custom_icon, f"<custom{custom_str}>", custom_value)
        # add standard entries, set current index
        self.setCurrentIndex(0)
        if initial is not NO_CHANGE and initial is not DEFAULT:
            self.setCurrentIndex(1)
        for i in range(1, 4):
            self.addItem(self._getIcon(i), str(i), float(i))
            if initial == i:
                self.setCurrentIndex(self.count() - 1)
        # enable custom dialog
        self.activated.connect(self._onActivated)

    def value(self : Self) -> NoChange | Default | float | int:
        return self.itemData(self.currentIndex(), Qt.ItemDataRole.UserRole)

    def _onActivated(self : Self, index : int) -> None:
        if self.currentText().startswith("<custom"):
            dialog = FloatDialog(title="Line Width", parent=self)
            if dialog.exec():
                w = dialog.value()
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
