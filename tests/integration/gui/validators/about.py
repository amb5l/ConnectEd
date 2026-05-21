"""Help → About validation."""

from PyQt6.QtWidgets import QMessageBox

from ConnectEd.core.defs import APP_NAME
from ConnectEd.scripting import Action, Menu, MenuBar, Window
from ConnectEd.scripting.qt.modal import activeModal, modalBodyText, withModal


def inspectHelpAboutDialog() -> None:
    modal = activeModal()
    assert modal is not None, "no active modal after Help → About"

    assert isinstance(modal, QMessageBox), (
        f"expected QMessageBox, got {type(modal).__name__}"
    )
    try:
        assert modal.text() == APP_NAME

        title = modal.windowTitle()
        assert title == "About", f"unexpected dialog title: {title!r}"
        body = modalBodyText(modal)
        assert APP_NAME in body, f"{APP_NAME!r} not in dialog body: {body!r}"

        ok = modal.button(QMessageBox.StandardButton.Ok)
        assert ok is not None, "About dialog has no OK button"
    finally:
        modal.accept()


def validateHelpAbout(window : Window) -> None:
    connected_bar = window.menuBar()
    assert connected_bar is not None
    assert connected_bar.isVisible()
    assert isinstance(connected_bar, MenuBar)

    help_menu = connected_bar.getMenus()["Help"]
    assert isinstance(help_menu, Menu)

    about = help_menu.getAction("About")
    assert about is not None, "About action not found"
    assert about.isEnabled()
    assert isinstance(about, Action)

    withModal(about.trigger, inspectHelpAboutDialog)
