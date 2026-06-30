"""Regression: moveRestore must round-trip moveSave for origin-pivot items."""

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


def test_rectangle_move_save_restore_roundtrip(connect_ed_app : ConnectEdApp) -> None:
    rect = BlockItem(QPointF(100.0, 100.0), QPointF(200.0, 160.0))
    assert rect.pos() != rect.scenePos()

    saved = rect.moveSave()
    rect.moveBy(30.0, -12.0)
    assert rect.scenePos() != saved

    rect.moveRestore(saved)
    assert rect.scenePos() == saved
