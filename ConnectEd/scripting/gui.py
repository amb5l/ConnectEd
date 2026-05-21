"""ConnectEd-aware GUI scripting driver."""

from typing import Self

from ..widgets.window import Window
from ..widgets.window.menu_bar import MenuBar

from .qt import QtScripting
from .qt.mouse import MouseMixin


class Gui(QtScripting, MouseMixin):
    """ConnectEd types, accessors, and QTest mouse delivery."""

    def __init__(self : Self, window : Window) -> None:
        super().__init__(window)

    def window(self : Self) -> Window:
        return self._window  # type: ignore[return-value]

    def menuBar(self : Self) -> MenuBar | None:
        return self.window().menuBar()


def gui(window : Window) -> Gui:
    return Gui(window)
