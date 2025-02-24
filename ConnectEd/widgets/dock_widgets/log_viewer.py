from ...core.logger import add_log_viewer_handler
from .text_viewer   import TextViewer


class LogViewer(TextViewer):
    WINDOW_TITLE = 'Log'

    def __init__(self, parent=None):
        super().__init__(parent)
        self.handler = add_log_viewer_handler(self.text_view)
