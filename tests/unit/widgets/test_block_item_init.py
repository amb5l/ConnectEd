"""Regression: BlockItem property texts must not read mirror state before init."""

import pytest

from PyQt6.QtCore    import QObject, QPointF, pyqtSignal
from PyQt6.QtWidgets import QApplication

from ConnectEd.app           import ConnectEdApp
from ConnectEd.core.settings import Settings

from ConnectEd.widgets.graphics.items.block     import BlockItem
from ConnectEd.widgets.graphics.items.block_pin import BlockPinItem
from ConnectEd.widgets.graphics.scenes.diagram  import DiagramScene

from ConnectEd.widgets.graphics.scenes.diagram.cmd.block_pin import \
    CmdDeleteBlockPin


@pytest.fixture
def connect_ed_app() -> ConnectEdApp:
    app = QApplication.instance()
    if not isinstance(app, ConnectEdApp):
        app = ConnectEdApp()
    assert isinstance(app, ConnectEdApp)

    class _FakeSettings(QObject):
        changed = pyqtSignal(str)

        def get(self, path : str, default=None):
            return default

    app.setSettings(_FakeSettings())
    return app


def test_block_item_set_label_after_init(connect_ed_app : ConnectEdApp) -> None:
    block = BlockItem(QPointF(10.0, 20.0), QPointF(110.0, 80.0))
    block.setReference("U1")
    block.setName("MyBlock")
    assert block.mirrorH() is False
    assert block.reference() == "U1"
    assert block.name() == "MyBlock"


def test_delete_block_pin_leaves_the_scene(
    connect_ed_app : ConnectEdApp,
) -> None:
    connect_ed_app.setSettings(Settings())
    scene = DiagramScene(doc=None, fresh=False)
    block = BlockItem()
    pin   = BlockPinItem()
    scene.addItem(block)
    pin.setParentItem(block)
    cmd = CmdDeleteBlockPin(block, pin)
    cmd.redo()
    assert pin.scene() is None
    assert pin.parentItem() is None
    assert pin not in scene.items()
    cmd.undo()
    assert pin.parentItem() is block
    assert pin.scene() is scene
