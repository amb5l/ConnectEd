from typing import Self

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QWidget, QComboBox
from PyQt6.QtGui     import QIcon, QPixmap, QPainter, QPen

from .....core.icon import getFgBgColors

from ....graphics.items import NoChange, Default, DEFAULT, NO_CHANGE

from .. import CUSTOM_ICON_SIZE, NoChangeIcon, DefaultIcon, QueryIcon

from ..dialog import CustomLineWidthDialog


class LineWidthComboBox(QComboBox):
    WIDTHS = {
        "<no change>" : NO_CHANGE,
        "<default>"   : DEFAULT,
        "<custom>"    : "placeholder",
        "1"           : 1,
        "2"           : 2,
        "3"           : 3
    }

    def __init__(
        self      : Self,
        initial   : NoChange | Default | float | int,
        default   : Default | float | int,
        no_change : NoChange | Default | float | int | None = None,
        parent    : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setIconSize(CUSTOM_ICON_SIZE)
        if isinstance(default, float | int):
            default_icon = self.getIcon(default)
            default_str = f" = {default}"
        else:
            default_icon = DefaultIcon().get()
            default_str = ""
        if isinstance(no_change, float | int):
            no_change_icon = self.getIcon(no_change)
            no_change_str = f" = {no_change}"
        elif no_change is DEFAULT:
            no_change_icon = default_icon
            no_change_str = f" = default{default_str}"
        else:
            no_change_icon = NoChangeIcon().get()
            no_change_str = ""
        for i, (k, v) in enumerate(self.WIDTHS.items()):
            match k:
                case "<no change>":
                    if no_change is None and initial is not NO_CHANGE:
                        continue
                    icon = no_change_icon
                    text = f"<no change{no_change_str}>"
                case "<default>":
                    icon = default_icon
                    text = f"<default{default_str}>"
                case "<custom>":
                    icon = QueryIcon().get()
                    text = k
                case _:
                    icon = self.getIcon(v)
                    text = f"{v}"
            self.addItem(icon, text)
            if initial == v:
                self.setCurrentIndex(i)
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.activated.connect(self.onActivated)

    def onActivated(self : Self, index : int) -> None:
        keys = list(self.WIDTHS.keys())
        if keys[index].startswith("<custom"):
            dialog = CustomLineWidthDialog(parent=self)
            if dialog.exec():
                w = dialog.getChoice()
                self.setItemText(
                    index,
                    f"<custom = {w}>" if w is not None else "<custom>"
                )
                self.setItemIcon(
                    index,
                    QueryIcon().get() if w is None else self.getIcon(w)
                )

    def getIcon(self : Self, width : float | int) -> QIcon:
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

    def getChoice(self : Self) -> float | None | NoChange:
        text = self.currentText()
        if text.startswith("<no change"):
            r = NO_CHANGE
        elif text.startswith("<default"):
            r = DEFAULT
        else:
            try:
                r = float(text)
                if r < 0:
                    r = None
            except ValueError:
                r = None
        return r
