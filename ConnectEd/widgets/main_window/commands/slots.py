from PyQt6.QtWidgets import QMessageBox

from ....core import logger
from ....widgets import Drawing

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....widgets.main_window import MainWindow

class Slots:
    _parent : 'MainWindow'

    def __init__(self : 'Slots', parent : 'MainWindow') -> None:
        self._parent = parent

    def fileExit(self : 'Slots') -> None:
        self._parent.close()

    def viewZoomIn(self : 'Slots') -> None:
        current_sub_window = self._parent.mdi_area.currentSubWindow()
        current_widget = current_sub_window.widget()
        if isinstance(current_widget, Drawing):
            current_widget.viewZoomIn()

    def viewZoomOut(self : 'Slots') -> None:
        current_sub_window = self._parent.mdi_area.currentSubWindow()
        current_widget = current_sub_window.widget()
        if isinstance(current_widget, Drawing):
            current_widget.viewZoomOut()

    def windowMessages(self : 'Slots') -> None:
        self._parent.msg_viewer.show()

    def windowLog(self : 'Slots') -> None:
        self._parent.log_viewer.show()

    def helpAbout(self : 'Slots') -> None:
        logger.debug('helpAbout')
        QMessageBox.about(self._parent, 'About', 'ConnectEd')
