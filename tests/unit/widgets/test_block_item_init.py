"""Regression: BlockItem property texts must not read mirror state before init."""

import pytest
from PyQt6.QtCore    import QObject, QPointF, pyqtSignal
from PyQt6.QtWidgets import QApplication

from ConnectEd.app import ConnectEdApp
from ConnectEd.widgets.graphics.items.block import BlockItem


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
    block.setLabel("U1")
    block.setName("MyBlock")
    assert block.mirrorH() is False
    assert block.label() == "U1"
    assert block.name() == "MyBlock"
