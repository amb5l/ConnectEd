from PyQt6.QtWidgets import QDockWidget

from ...core        import LOG_FILENAME
from ..text_viewer  import TextViewer
from ...core.logger import LogViewerHandler, add_log_viewer_handler


class LogViewer(QDockWidget):
    text_viewer : TextViewer
    handler     : LogViewerHandler

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Log')
        self.text_viewer = TextViewer(self, LOG_FILENAME)
        self.setWidget(self.text_viewer)
        self.handler = add_log_viewer_handler(self.text_viewer)
