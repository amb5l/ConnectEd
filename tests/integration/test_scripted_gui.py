from typing import Self

import ConnectEd.scripting as cs

from integration.gui.specs import MAIN_WIDGETS, MENUS_STARTUP

from integration.gui.validators import (
    validateDrawing,
    validateHelpAbout,
    validateMainWindow,
    validateMainWidgets,
    validateMenus,
)


def test(app : cs.App) -> None:
    print("test started")

    assert isinstance(app, cs.App)
    assert app.cli() is False

    window = validateMainWindow(app)
    validateMainWidgets(window, MAIN_WIDGETS)
    validateMenus(window, MENUS_STARTUP)
    validateHelpAbout(window)
    validateDrawing(window)

    print("test finished")


class TestScriptedGUI:
    def test_scripted_gui(self : Self) -> None:
        cs.run(test, ["--nosplash"])


if __name__ == "__main__":
    cs.run(test, ["--nosplash"])
