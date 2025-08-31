from PyQt6.QtWidgets import QStatusBar, QLabel

from typing import Self

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import Window


class StatusBar(QStatusBar):
    xy     : QLabel
    zoom   : QLabel
    select : QLabel
    msg    : QLabel

    def __init__(self : Self, parent : "Window") -> None:
        super().__init__(parent)
        self.msg    = QLabel("Initializing...")
        self.tip    = QLabel("")
        self.xy     = QLabel("?,?")
        self.zoom   = QLabel("? %")
        self.select = QLabel("0 items selected")
        self.addWidget(self.msg)
        self.addWidget(self.tip)
        self.addPermanentWidget(self.xy)
        self.addPermanentWidget(self.zoom)
        self.addPermanentWidget(self.select)
