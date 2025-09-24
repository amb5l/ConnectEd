from typing  import Self
from logging import Logger

from PyQt6.QtCore    import QCoreApplication
from PyQt6.QtWidgets import QApplication

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .core.nv        import Settings
    from .core.db        import Model
    from .widgets.window import Window


class ConnectEdApp:
    # Instance attributes
    _logger   : "Logger | None"
    _settings : "Settings | None"
    _model    : "Model | None"

    def __init__(self : Self) -> None:
        self._logger   = None
        self._settings = None
        self._model    = None

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

    @staticmethod
    def instance() -> "ConnectEdCliApp | ConnectEdGuiApp | None":
        app = QApplication.instance()
        if app is None:
            app = QCoreApplication.instance()
        return app


class ConnectEdCliApp(ConnectEdApp, QCoreApplication):
    def __init__(self : Self, argv : list[str]) -> None:
        QCoreApplication.__init__(self, argv)
        ConnectEdApp.__init__(self)

    def window(self : Self) -> None:
        raise RuntimeError("CLI applications do not support GUI windows")

    def setWindow(self : Self, _window : "Window") -> None:
        raise RuntimeError("CLI applications do not support GUI windows")


class ConnectEdGuiApp(ConnectEdApp, QApplication):
    # Instance attributes
    _window : "Window | None"

    def __init__(self : Self, argv : list[str]) -> None:
        QApplication.__init__(self, argv)
        ConnectEdApp.__init__(self)
        self._window = None

    def window(self : Self) -> "Window":
        return self._window

    def setWindow(self : Self, window : "Window") -> None:
        self._window = window


def app() -> ConnectEdCliApp | ConnectEdGuiApp:
    return ConnectEdApp.instance()


def logger() -> Logger | None:
    return app().logger()


def settings() -> "Settings | None":
    return app().settings()


def model() -> "Model | None":
    return app().model()


def window() -> "Window | None":
    return app().window()
