from ..core.logger   import add_log_viewer_handler
from .text_view_dock import TextViewDockWidget


class LogViewDock(TextViewDockWidget):
    WINDOW_TITLE = 'Log'

    def __init__(self, parent=None):
        super().__init__(parent)
        self.handler = add_log_viewer_handler(self.text_view)
