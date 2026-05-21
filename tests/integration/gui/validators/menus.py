"""Menu tree validation: ConnectEd API (contract) and QMenuBar walk (Qt)."""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMenu, QMenuBar, QWidget

from ConnectEd.scripting import Menu, MenuBar, Window


def _menuTitle(menu : QMenu) -> str:
    return menu.title().replace("&", "")


def _actionName(action : QAction) -> str:
    return action.text().replace("&", "").replace("...", "")


def _assertActions(menu : Menu, *names : str) -> None:
    actions = menu.getActions()
    for name in names:
        assert name in actions, f"{name!r} not in {list(actions.keys())}"


def _validateMenuContract(menu : Menu, menu_spec : list) -> None:
    for menu_item in menu_spec:
        if isinstance(menu_item, str):
            _assertActions(menu, menu_item)
        elif isinstance(menu_item, dict):
            sub_menus = menu.getSubMenus()
            for sub_name, sub_spec in menu_item.items():
                assert sub_name in sub_menus, (
                    f"{sub_name!r} not in {list(sub_menus.keys())}"
                )
                _validateMenuContract(sub_menus[sub_name], sub_spec)
        else:
            raise TypeError(f"unexpected menu spec item: {menu_item!r}")


def _qtTopMenu(menu_bar : QMenuBar, title : str) -> QMenu | None:
    for bar_action in menu_bar.actions():
        sub_menu = bar_action.menu()
        if sub_menu is not None and _menuTitle(sub_menu) == title:
            return sub_menu
    return None


def _qtSubMenu(menu : QMenu, title : str) -> QMenu | None:
    for menu_action in menu.actions():
        sub_menu = menu_action.menu()
        if sub_menu is not None and _menuTitle(sub_menu) == title:
            return sub_menu
    return None


def _qtLeafAction(menu : QMenu, name : str) -> QAction | None:
    for menu_action in menu.actions():
        if menu_action.menu() is None and _actionName(menu_action) == name:
            return menu_action
    return None


def _validateMenuQt(menu : QMenu, menu_spec : list) -> None:
    for menu_item in menu_spec:
        if isinstance(menu_item, str):
            assert _qtLeafAction(menu, menu_item) is not None, (
                f"{menu_item!r} not found in Qt menu {menu.title()!r}"
            )
        elif isinstance(menu_item, dict):
            for sub_name, sub_spec in menu_item.items():
                sub_menu = _qtSubMenu(menu, sub_name)
                assert sub_menu is not None, (
                    f"{sub_name!r} not found in Qt submenu of {menu.title()!r}"
                )
                _validateMenuQt(sub_menu, sub_spec)
        else:
            raise TypeError(f"unexpected menu spec item: {menu_item!r}")


def _qtMenuBar(window : Window) -> QMenuBar:
    options = Qt.FindChildOption.FindChildrenRecursively
    qt_bar = QWidget.findChild(window, QMenuBar, options=options)  # type: ignore[arg-type]
    assert qt_bar is not None, "QMenuBar not found via Qt findChild"
    return qt_bar  # type: ignore[return-value]


def validateMenus(window : Window, menus : dict[str, list]) -> None:
    connected_bar = window.menuBar()
    assert connected_bar is not None
    assert isinstance(connected_bar, MenuBar)

    for menu_name, menu_spec in menus.items():
        assert menu_name in connected_bar.getMenus(), (
            f"{menu_name!r} not in {list(connected_bar.getMenus().keys())}"
        )
        _validateMenuContract(connected_bar.getMenus()[menu_name], menu_spec)

    qt_bar = _qtMenuBar(window)
    assert qt_bar is connected_bar, (
        "ConnectEd menuBar is not the same object as the Qt QMenuBar"
    )

    for menu_name, menu_spec in menus.items():
        qt_menu = _qtTopMenu(qt_bar, menu_name)
        assert qt_menu is not None, (
            f"{menu_name!r} not found on QMenuBar (Qt walk)"
        )
        _validateMenuQt(qt_menu, menu_spec)
