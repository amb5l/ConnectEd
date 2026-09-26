"""GUI diagram creation: place items and check the scene graph."""

from __future__ import annotations

from enum import Enum

from PyQt6.QtCore    import Qt, QPoint, QPointF
from PyQt6.QtWidgets import QListWidget, QMdiSubWindow, QMenu
from PyQt6.QtTest    import QTest

from ConnectEd.app                                  import settings
from ConnectEd.scripting                            import Window, gui
from ConnectEd.core.types                           import RectHandleId
from ConnectEd.scripting.gui                        import Gui
from integration.gui.text_theme                     import assert_text_theme
from ConnectEd.scripting.qt.modal                   import activeModal, withModal
from ConnectEd.widgets.dialogs.file                 import FileNewDialog
from ConnectEd.widgets.graphics.items.block         import BlockItem
from ConnectEd.widgets.graphics.items.grip          import GripItem
from ConnectEd.widgets.graphics.items.handle        import HandleItem
from ConnectEd.widgets.graphics.items.property_text import PropertyTextItem
from ConnectEd.widgets.graphics.views.diagram       import DiagramView

from ConnectEd.widgets.graphics.views.diagram.mouse import MouseState


class CommandInput(Enum):
    """How the diagram test issues menu commands."""

    SHORTCUT = "shortcut"
    MENU     = "menu"


_DOC_TYPE = "HDL Schematic Diagram"

# cleat, origin — from PartItemMixin._PROPERTY_TEXTS
_PROPERTY_TEXTS : dict[str, tuple[RectHandleId, RectHandleId]] = {
    "Label" : (RectHandleId.TOP_LEFT,    RectHandleId.BOTTOM_LEFT),
    "Name"  : (RectHandleId.BOTTOM_LEFT, RectHandleId.TOP_LEFT),
}


def _status(window : Window) -> str:
    bar = window.statusBar()
    assert bar is not None
    return bar.status.text()


def _menu_named(driver : Gui, window : Window, title : str) -> QMenu:
    connected_bar = window.menuBar()
    assert connected_bar is not None
    menu = driver.menu(connected_bar, title)
    assert menu is not None, f"no {title} menu"
    return menu


def _open_menu(driver : Gui, window : Window, menu : str) -> QMenu:
    """Click the menu bar so the popup is open before a modal command."""
    connected_menu = _menu_named(driver, window, menu)
    connected_bar = window.menuBar()
    assert connected_bar is not None
    bar_action = next(
        candidate for candidate in connected_bar.actions()
        if candidate.menu() is connected_menu
    )
    driver.mouseClick(
        connected_bar, connected_bar.actionGeometry(bar_action).center()
    )
    assert connected_menu.isVisible(), f"{menu} menu did not open"
    return connected_menu


def _fire(
    driver : Gui,
    window : Window,
    menu   : str,
    name   : str,
    mode   : CommandInput,
) -> None:
    """Send the shortcut, or click an item in a menu that is already open."""
    connected_menu = _menu_named(driver, window, menu)
    action = driver.action(connected_menu, name)
    assert action is not None and action.isEnabled(), f"{menu} / {name} is not enabled"
    if mode is CommandInput.SHORTCUT:
        sequence = action.shortcut()
        assert not sequence.isEmpty(), f"{menu} / {name} has no shortcut"
        QTest.keySequence(window, sequence)
        driver.processEvents()
        return
    assert connected_menu.isVisible(), f"{menu} menu is not open"
    driver.mouseClick(
        connected_menu, connected_menu.actionGeometry(action).center()
    )
    driver.processEvents()


def _invoke(
    driver : Gui,
    window : Window,
    menu   : str,
    name   : str,
    mode   : CommandInput,
) -> None:
    """Issue a menu command by shortcut or by clicking the open menu."""
    if mode is CommandInput.MENU:
        _open_menu(driver, window, menu)
    _fire(driver, window, menu, name, mode)


def _new_diagram(driver : Gui, window : Window, mode : CommandInput) -> None:
    def choose() -> None:
        modal = activeModal()
        assert isinstance(modal, FileNewDialog), (
            f"expected FileNewDialog, got {type(modal).__name__}"
        )
        lists = modal.findChildren(QListWidget)
        assert len(lists) == 1
        widget = lists[0]
        target = None
        for i in range(widget.count()):
            item = widget.item(i)
            if item is not None and item.text() == _DOC_TYPE:
                target = item
                break
        assert target is not None, f"{_DOC_TYPE!r} not in New Document list"
        try:
            # Clicks land on the viewport; the list widget itself does not.
            driver.mouseClick(
                widget.viewport(), widget.visualItemRect(target).center()
            )
            assert widget.selectedItems(), "document type was not selected"
            ok = modal._ok_cancel_layout._ok_button
            assert ok.isEnabled()
            driver.mouseClick(ok, QPoint(ok.width() // 2, ok.height() // 2))
        finally:
            if modal.isVisible():
                modal.reject()

    if mode is CommandInput.MENU:
        _open_menu(driver, window, "File")
    withModal(lambda: _fire(driver, window, "File", "New", mode), choose)
    driver.processEvents()


def _active_diagram_view(driver : Gui) -> DiagramView:
    mdi = driver.window().mdiArea()
    assert mdi is not None
    sub = mdi.activeSubWindow()
    assert isinstance(sub, QMdiSubWindow), "no diagram subwindow after New"
    view = sub.widget()
    assert isinstance(view, DiagramView), (
        f"expected DiagramView, got {type(view).__name__}"
    )
    return view


def _place_block(
    driver : Gui,
    window : Window,
    view   : DiagramView,
    mode   : CommandInput,
) -> None:
    view.viewZoomAll()
    driver.processEvents()

    _invoke(driver, window, "Place", "Block", mode)
    assert _status(window) == "Place Block: pick the first point", _status(window)

    p1 = QPointF(100.0, 100.0)
    p2 = QPointF(300.0, 200.0)
    v1 = driver.viewPos(view, p1)
    v2 = driver.viewPos(view, p2)
    drag = settings().get("prefs/mouse/drag") or 5
    assert (v2 - v1).manhattanLength() > drag
    # A menu or shortcut can leave the view in BAD_PRESS. The next left click
    # must still start placement.
    view._mouse_state = MouseState.BAD_PRESS
    _click_canvas(driver, view, v1)
    assert _status(window) == "Place Block: pick the second point", (
        f"first click left status {_status(window)!r}"
    )
    _click_canvas(driver, view, v2)
    driver.processEvents()


def _click_canvas(driver : Gui, view : DiagramView, pos : QPoint) -> None:
    viewport = view.viewport()
    assert viewport is not None
    QTest.mouseClick(
        viewport,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
        pos,
    )
    driver.processEvents()


def _block_on_scene(view : DiagramView) -> BlockItem:
    scene = view.scene()
    assert scene is not None
    blocks = [
        item for item in scene.items()
        if isinstance(item, BlockItem) and item.parentItem() is None
    ]
    assert len(blocks) == 1, f"expected 1 block, found {len(blocks)}"
    block = blocks[0]
    assert block.scene() is scene
    return block


def _assert_block_texts(block : BlockItem) -> None:
    handles = {
        child.id() : child
        for child in block.childItems()
        if isinstance(child, HandleItem)
    }
    assert set(handles) == set(RectHandleId), (
        f"block handles {set(handles)!r}"
    )
    for handle_id, handle in handles.items():
        assert handle.parentItem() is block
        grips = [
            child for child in handle.childItems()
            if isinstance(child, GripItem)
        ]
        assert len(grips) == 1, f"{handle_id} grip count {len(grips)}"

    texts : dict[str, PropertyTextItem] = {}
    for handle in handles.values():
        for child in handle.childItems():
            if isinstance(child, PropertyTextItem):
                assert child.name() not in texts
                texts[child.name()] = child
                assert child.parentItem() is handle
                assert handle.parentItem() is block
    assert set(texts) == set(_PROPERTY_TEXTS), (
        f"property texts {set(texts)!r}"
    )
    for name, (cleat, origin) in _PROPERTY_TEXTS.items():
        text = texts[name]
        assert text.cleat() == cleat
        assert text.origin() == origin
        assert text.isVisible()
        parent = text.parentItem()
        assert isinstance(parent, HandleItem)
        assert parent.id() == cleat
        assert_text_theme(text, f"<{name}>")


def validateDiagram(
    window        : Window,
    command_input : CommandInput | None = None,
) -> None:
    """Create a schematic and place one block.

    ``command_input`` selects shortcuts or menu clicks. The default runs the
    check once with each.
    """
    modes = (command_input,) if command_input is not None else tuple(CommandInput)
    for mode in modes:
        driver = gui(window)
        _new_diagram(driver, window, mode)
        view = _active_diagram_view(driver)
        _place_block(driver, window, view, mode)
        _assert_block_texts(_block_on_scene(view))
