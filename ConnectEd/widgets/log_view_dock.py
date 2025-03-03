from typing import Optional

from PyQt6.QtWidgets import QWidget

from ..core.logger   import add_log_viewer_handler, LOG_FILENAME
from .text_view_dock import TextViewDockWidget


class LogViewDock(TextViewDockWidget):
    WINDOW_TITLE = 'Log'

    def __init__(
        self     : 'LogViewDock',
        parent   : Optional[QWidget] = None,
        filename : str = LOG_FILENAME
    ) -> None:
        super().__init__(parent, filename)
        self.handler = add_log_viewer_handler(self.text_view)
