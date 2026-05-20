from PyQt6.QtWidgets import QStatusBar, QLabel

from typing import Self

from ...core.check import checked

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import Window


class StatusBar(QStatusBar):
    status : QLabel
    xy     : QLabel
    zoom   : QLabel
    select : QLabel

    @checked
    def __init__(self : Self, parent : "Window") -> None:
        super().__init__(parent)
        self.status = QLabel("Initializing...")
        self.xy     = QLabel("?,?")
        self.zoom   = QLabel("? %")
        self.select = QLabel("0 items selected")
        self.addWidget(self.status)
        self.addPermanentWidget(self.xy)
        self.addPermanentWidget(self.zoom)
        self.addPermanentWidget(self.select)
