from __future__ import annotations

import os
import logging
import weakref

from typing import Self, Protocol

from .defs import APP_NAME, LOG_FILENAME


class RelativePathFormatter(logging.Formatter):
    def format(self : Self, record : logging.LogRecord) -> str:
        try:
            record.relpath = os.path.relpath(record.pathname)
        except ValueError:
            record.relpath = record.pathname
        return super().format(record)


class LogViewerProtocol(Protocol):
    _handler : LogViewerHandler

    def appendPlainText(self : Self, text : str) -> None:
        ...


class LogViewerHandler(logging.Handler):
    log_viewer : LogViewerProtocol

    def __init__(self : Self, log_viewer : LogViewerProtocol) -> None:
        super().__init__()
        self.log_viewer = weakref.proxy(log_viewer)
        self.log_viewer._handler = self

    def emit(self : Self, record : logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            self.log_viewer.appendPlainText(msg)
        except (ReferenceError, RuntimeError): # widget is gone
            logger.removeHandler(self)


logger = logging.getLogger(APP_NAME)
logger.setLevel(logging.DEBUG)

formatter = RelativePathFormatter(
    "%(asctime)s: %(relpath)50s: %(funcName)24s(): %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

file_handler = logging.FileHandler(LOG_FILENAME)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

def addLogViewerHandler(log_viewer : LogViewerProtocol) -> LogViewerHandler:
    log_viewer_handler = LogViewerHandler(log_viewer)
    log_viewer_handler.setLevel(logging.DEBUG)  # Or whatever level you prefer
    log_viewer_handler.setFormatter(formatter)  # Use the same formatter as other handlers
    logger.addHandler(log_viewer_handler)
    return log_viewer_handler


# TODO review logging levels for console, file, viewer
