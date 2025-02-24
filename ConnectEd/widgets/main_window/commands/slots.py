from PyQt6.QtWidgets import QDialog, QMessageBox

from ....core import logger

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....widgets.main_window import MainWindow

class Slots:
    _parent : 'MainWindow'

    def __init__(self : 'Slots', parent : 'MainWindow') -> None:
        self._parent = parent

    def fileExit(self):
        self._parent.close()

    def windowMessages(self):
        self._parent.msg_viewer.show()

    def windowLog(self):
        self._parent.log_viewer.show()

    def helpAbout(self):
        logger.debug('helpAbout')
        QMessageBox.about(self._parent, 'About', 'ConnectEd')
