"""GUI diagram creation: place items and check the scene graph."""

from __future__ import annotations

from PyQt6.QtCore import QPoint, QPointF
from PyQt6.QtWidgets import QListWidget, QMdiSubWindow

from ConnectEd.app import settings
from ConnectEd.core.types import RectHandleId
from ConnectEd.scripting import Window, gui
from ConnectEd.scripting.qt.modal import activeModal, withModal
from ConnectEd.widgets.dialogs.file import FileNewDialog
from ConnectEd.widgets.graphics.items.block import BlockItem
from ConnectEd.widgets.graphics.items.grip import GripItem
from ConnectEd.widgets.graphics.items.handle import HandleItem
from ConnectEd.widgets.graphics.items.property_text import PropertyTextItem
from ConnectEd.widgets.graphics.views.diagram import DiagramView

from integration.gui.text_theme import assert_text_theme


_DOC_TYPE = "HDL Schematic Diagram"

# cleat, origin — from PartItemMixin._PROPERTY_TEXTS
_PROPERTY_TEXTS : dict[str, tuple[RectHandleId, RectHandleId]] = {
    "Label" : (RectHandleId.TOP_LEFT,    RectHandleId.BOTTOM_LEFT),
    "Name"  : (RectHandleId.BOTTOM_LEFT, RectHandleId.TOP_LEFT),
}


def _menu_action(menu, name : str):
    for action in menu.actions():
        if action.isSeparator() or action.menu() is not None:
            continue
        text = action.text().replace("&", "").replace("...", "")
        if text == name:
            return action
    return None


def _new_diagram(driver, window : Window) -> None:
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

    connected_bar = window.menuBar()
    assert connected_bar is not None
    new = _menu_action(connected_bar.getMenus()["File"], "New")
    assert new is not None
    withModal(new.trigger, choose)
    driver.processEvents()


def _active_diagram_view(driver) -> DiagramView:
    mdi = driver.window().mdiArea()
    assert mdi is not None
    sub = mdi.activeSubWindow()
    assert isinstance(sub, QMdiSubWindow), "no diagram subwindow after New"
    view = sub.widget()
    assert isinstance(view, DiagramView), (
        f"expected DiagramView, got {type(view).__name__}"
    )
    return view


def _place_block(driver, window : Window, view : DiagramView) -> None:
    sub = driver.window().mdiArea().activeSubWindow()
    assert isinstance(sub, QMdiSubWindow)
    driver.window().mdiArea().activateSubWindow(sub)
    view.setFocus()
    view.viewZoomAll()
    driver.processEvents()

    place = window.menuBar()
    assert place is not None
    block_action = _menu_action(place.getMenus()["Place"], "Block")
    assert block_action is not None and block_action.isEnabled()
    block_action.trigger()
    driver.processEvents()

    p1 = QPointF(100.0, 100.0)
    p2 = QPointF(300.0, 200.0)
    v1 = driver.viewPos(view, p1)
    v2 = driver.viewPos(view, p2)
    drag = settings().get("prefs/mouse/drag") or 5
    assert (v2 - v1).manhattanLength() > drag
    driver.mouseDrag(view, v1, v2)
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


def validateDiagram(window : Window) -> None:
    """Create a schematic and place one block."""
    driver = gui(window)
    _new_diagram(driver, window)
    view = _active_diagram_view(driver)
    _place_block(driver, window, view)
    _assert_block_texts(_block_on_scene(view))
