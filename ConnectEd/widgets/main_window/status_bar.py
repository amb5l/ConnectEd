from PyQt6.QtWidgets import QStatusBar, QLabel

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import MainWindow


class StatusBar(QStatusBar):
    xy     : QLabel
    zoom   : QLabel
    select : QLabel
    msg    : QLabel

    def __init__(self : 'StatusBar', parent : 'MainWindow') -> None:
        super().__init__(parent)
        self.xy     = QLabel('?,?')
        self.zoom   = QLabel('? %')
        self.select = QLabel('0 items selected')
        self.msg    = QLabel('Initializing...')
        self.addPermanentWidget(self.xy)
        self.addPermanentWidget(self.zoom)
        self.addPermanentWidget(self.select)
        self.addWidget(self.msg)
