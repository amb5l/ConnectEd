from typing  import Self
from logging import Logger

from PyQt6.QtCore    import QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication

from .core.check import checked

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .core.settings  import Settings
    from .core.db        import Model
    from .widgets.window import Window


class ConnectEdApp(QApplication):
    class Ready(QObject):
        window = pyqtSignal()
        splash = pyqtSignal()

    # instance attributes
    _logger   : "Logger | None"
    _settings : "Settings | None"
    _model    : "Model | None"
    _window   : "Window | None"
    _cli      : bool
    ready     : Ready

    @checked
    def __init__(self   : Self, cli : bool = False) -> None:
        super().__init__([])
        self._logger   = None
        self._settings = None
        self._model    = None
        self._window   = None
        self._cli      = cli
        self.ready     = self.Ready()

    @checked
    def logger(self : Self) -> "Logger":
        return self._logger

    @checked
    def setLogger(self : Self, logger : "Logger") -> None:
        self._logger = logger

    @checked
    def settings(self : Self) -> "Settings":
        return self._settings

    @checked
    def setSettings(self : Self, settings : "Settings") -> None:
        self._settings = settings

    @checked
    def model(self : Self) -> "Model":
        return self._model

    @checked
    def setModel(self : Self, model : "Model") -> None:
        self._model = model

    @checked
    def window(self : Self) -> "Window | None":
        return None if self._cli else self._window

    @checked
    def setWindow(self : Self, window : "Window") -> None:
        if self._cli:
            return  # Ignore window setting in CLI mode
        self._window = window

    @checked
    def cli(self : Self) -> bool:
        return self._cli

    @checked
    def setCli(self : Self, cli : bool) -> None:
        self._cli = cli


@checked
def app() -> "ConnectEdApp":
    return ConnectEdApp.instance()


@checked
def logger() -> Logger | None:
    return app().logger()


@checked
def settings() -> "Settings | None":
    return app().settings()


@checked
def model() -> "Model | None":
    return app().model()


@checked
def window() -> "Window | None":
    return app().window()
