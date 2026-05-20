from typing import Self

import ConnectEd.scripting as cs

from ConnectEd.widgets.menu import Menu


def assert_actions(menu : Menu, *names : str) -> None:
    actions = menu.getActions()
    for name in names:
        assert name in actions, f"{name!r} not in {list(actions.keys())}"


def test(app : cs.App) -> None:

    print("test started")

    assert isinstance(app, cs.App)

    # verify we are running in GUI mode
    assert app.cli() == False

    # get main window
    window = app.window()
    assert window is not None
    assert window.isVisible()

    # verify existence and visibility of menu bar, dock widgets, and MDI area
    menu_bar = window.menuBar()
    assert menu_bar is not None
    assert menu_bar.isHidden() == False
    navigator_dock = window.navigatorDock()
    assert navigator_dock is not None
    assert navigator_dock.isHidden() == False
    messages_viewer = window.messagesDock()
    assert messages_viewer is not None
    assert messages_viewer.isHidden() == False
    transcript_viewer = window.transcriptDock()
    assert transcript_viewer is not None
    assert transcript_viewer.isHidden() == False
    log_viewer = window.logDock()
    assert log_viewer is not None
    assert log_viewer.isHidden() == False
    mdi_area = window.mdiArea()
    assert mdi_area is not None
    assert mdi_area.isHidden() == False

    menus = menu_bar.getMenus()

    # File menu
    assert "File" in menus
    file_menu = menus["File"]
    file_new_menu = file_menu.getSubMenus()["New"]
    assert_actions(
        file_menu,
        "Open", "Save", "Save As", "Close", "Exit",
    )
    assert_actions(file_new_menu, "Design", "Library")

    # Edit menu
    assert "Edit" in menus
    edit_menu = menus["Edit"]
    assert_actions(
        edit_menu,
        "Cancel",
        "Undo", "Redo",
        "Cut", "Copy", "Paste", "Delete", "Duplicate",
        "Select Area", "Select All",
        "Properties", "Appearance",
        "Query",
    )

    # View menu
    assert "View" in menus
    view_menu = menus["View"]
    view_theme_menu = view_menu.getSubMenus()["Theme"]
    assert_actions(
        view_menu,
        "Zoom All", "Zoom Sheet", "Zoom Area", "Zoom In", "Zoom Out",
        "Pan", "Pan Up", "Pan Down", "Pan Left", "Pan Right",
        "Grid Display", "Grid Snap",
    )
    assert_actions(view_theme_menu, "Dark", "Light Mono")

    # Place menu (empty until a diagram/symbol window is active)
    assert "Place" in menus
    place_menu = menus["Place"]
    assert place_menu.isEnabled() == False
    assert place_menu.getActions() == {}

    # Window menu
    assert "Window" in menus
    window_menu = menus["Window"]
    assert_actions(
        window_menu,
        "Next", "Previous",
        "Navigator", "Messages", "Transcript", "Log",
    )

    # Help menu
    assert "Help" in menus
    help_menu = menus["Help"]
    assert_actions(help_menu, "About")

    print("test finished")


class TestScriptedGUI:
    def test_scripted_gui(self : Self) -> None:
        cs.run(test, ["--nosplash"])


if __name__ == "__main__":
    cs.run(test, ["--nosplash"])
