from typing import Self, Optional

from PyQt6.QtWidgets import QWidget

from ..core.log import addLogViewerHandler, LOG_FILENAME
from .text_view import TextViewDockWidget


class LogViewDock(TextViewDockWidget):
    WINDOW_TITLE = 'Log'

    def __init__(
        self     : Self,
        parent   : Optional[QWidget] = None,
        filename : str = LOG_FILENAME
    ) -> None:
        super().__init__(parent, filename)
        self.handler = addLogViewerHandler(self.text_view)
