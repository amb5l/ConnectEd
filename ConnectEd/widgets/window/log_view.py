from typing import Self

from PyQt6.QtWidgets import QWidget

from ...app import logger

from ...core.check import checked
from ...core.log   import LOG_FILENAME, addLogViewerHandler, LogViewerHandler

from .text_view  import TextView, TextViewDockWidget


class LogView(TextView):
    _handler : LogViewerHandler

    @checked
    def __init__(
        self     : Self,
        parent   : QWidget,
        filename : str | None = None
    ) -> None:
        super().__init__(parent, filename)
        self._handler = addLogViewerHandler(self)

    def __del__(self : Self) -> None:
        if hasattr(self, "_handler") and self._handler:
            try:
                logger().removeHandler(self._handler)
            except RuntimeError: # workaround for Qt cleanup
                pass


class LogViewDock(TextViewDockWidget):
    WINDOW_TITLE = "Log"

    @checked
    def __init__(
        self     : Self,
        parent   : QWidget | None = None,
        filename : str = LOG_FILENAME
    ) -> None:
        super().__init__(parent, filename)
