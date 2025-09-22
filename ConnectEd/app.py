from typing  import Self
from logging import Logger

from PyQt6.QtWidgets import QApplication

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .core.nv        import Settings
    from .core.db        import Model
    from .widgets.window import Window


class ConnectEdApp(QApplication):
    # instance attributes
    logger   : "Logger | None"
    settings : "Settings | None"
    model    : "Model | None"
    window   : "Window | None"

    def __init__(self : Self, argv : list[str]) -> None:
        super().__init__(argv)
        self.logger   = None
        self.settings = None
        self.model    = None
        self.window   = None


def app() -> ConnectEdApp:
    return ConnectEdApp.instance()

def logger() -> Logger:
    return app().logger

def settings() -> "Settings":
    return app().settings

def model() -> "Model":
    return app().model

def window() -> "Window":
    return app().window
