from typing  import Self
from logging import Logger

from PyQt6.QtWidgets import QApplication

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .core.nv        import Settings
    from .core.db        import Model
    from .widgets.window import Window


class ConnectEdApp(QApplication):
    # Instance attributes
    _logger   : "Logger | None"
    _settings : "Settings | None"
    _model    : "Model | None"
    _window   : "Window | None"
    _cli      : bool

    def __init__(self : Self, argv : list[str], cli : bool = False) -> None:
        super().__init__(argv)
        self._logger   = None
        self._settings = None
        self._model    = None
        self._window   = None
        self._cli      = cli

    def logger(self : Self) -> "Logger":
        return self._logger

    def setLogger(self : Self, logger : "Logger") -> None:
        self._logger = logger

    def settings(self : Self) -> "Settings":
        return self._settings

    def setSettings(self : Self, settings : "Settings") -> None:
        self._settings = settings

    def model(self : Self) -> "Model":
        return self._model

    def setModel(self : Self, model : "Model") -> None:
        self._model = model

    def window(self : Self) -> "Window | None":
        return None if self._cli else self._window

    def setWindow(self : Self, window : "Window") -> None:
        if self._cli:
            return  # Ignore window setting in CLI mode
        self._window = window

    def cli(self : Self) -> bool:
        return self._cli

    def setCli(self : Self, cli : bool) -> None:
        self._cli = cli


def app() -> "ConnectEdApp":
    return ConnectEdApp.instance()


def logger() -> Logger | None:
    return app().logger()


def settings() -> "Settings | None":
    return app().settings()


def model() -> "Model | None":
    return app().model()


def window() -> "Window | None":
    return app().window()
