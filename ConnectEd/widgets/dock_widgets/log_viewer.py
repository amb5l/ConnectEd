from PyQt6.QtWidgets import QDockWidget
from PyQt6.QtGui     import QTextOption

from ...core            import LOG_FILENAME, logger
from ..text_file_viewer import TextFileViewer
from ...core.logger     import LogViewerHandler, add_log_viewer_handler


class LogViewer(QDockWidget):
    text_file_viewer : TextFileViewer
    handler          : LogViewerHandler

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Log')
        self.text_file_viewer = TextFileViewer(self, LOG_FILENAME)
        self.setWidget(self.text_file_viewer)
        self.handler = add_log_viewer_handler(self.text_file_viewer)
