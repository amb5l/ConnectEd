from PyQt6.QtWidgets import QMessageBox

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

    def viewZoomIn(self):
        current_widget = self._parent.mdi_area.currentSubWindow()
        if current_widget:
            current_widget.zoomIn()

    def viewZoomOut(self):
        current_widget = self._parent.mdi_area.currentSubWindow()
        if current_widget:
            current_widget.zoomOut()

    def windowMessages(self):
        self._parent.msg_viewer.show()

    def windowLog(self):
        self._parent.log_viewer.show()

    def helpAbout(self):
        logger.debug('helpAbout')
        QMessageBox.about(self._parent, 'About', 'ConnectEd')
