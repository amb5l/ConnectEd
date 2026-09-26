"""Main window shell validation."""

from ConnectEd.scripting import App, Window
from ConnectEd.core.defs import APP_NAME


def validateMainWindow(app : App) -> Window:
    window = app.window()
    assert window is not None
    assert window.isVisible()
    assert window.windowTitle() == APP_NAME
    return window
