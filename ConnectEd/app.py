from __future__ import annotations

from typing  import Self
from logging import Logger

from PyQt6.QtCore    import QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication

from .core.check    import checked
from .core.log      import logger as core_logger

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .core.settings  import Settings
    from .core.session   import Session
    from .widgets.window import Window

class ConnectEdApp(QApplication):
    class Ready(QObject):
        window = pyqtSignal()
        splash = pyqtSignal()

    # instance attributes
    _logger   : Logger
    _settings : Settings
    _session  : Session
    _window   : Window
    _cli      : bool
    ready     : Ready

    @checked
    def __init__(self   : Self, cli : bool = False) -> None:
        super().__init__([])
        self._logger = core_logger
        self._cli    = cli
        self.ready   = self.Ready()

    @checked
    def logger(self : Self) -> Logger:
        return self._logger

    @checked
    def setLogger(self : Self, logger : Logger) -> None:
        self._logger = logger

    @checked
    def settings(self : Self) -> Settings:
        return self._settings

    @checked
    def setSettings(self : Self, settings : Settings) -> None:
        self._settings = settings

    @checked
    def session(self : Self) -> Session:
        return self._session

    @checked
    def setSession(self : Self, session : Session) -> None:
        self._session = session

    @checked
    def window(self : Self) -> Window | None:
        return self._window

    @checked
    def setWindow(self : Self, window : Window) -> None:
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
def app() -> ConnectEdApp:
    if not isinstance(instance := ConnectEdApp.instance(), ConnectEdApp):
        raise RuntimeError("Bad instance")
    return instance


@checked
def logger() -> Logger:
    return app().logger()


@checked
def settings() -> Settings:
    return app().settings()


@checked
def session() -> Session:
    return app().session()


@checked
def window() -> Window:
    from .widgets.window import Window
    if not isinstance(w := app().window(), Window):
        raise TypeError("Bad window")
    return w
