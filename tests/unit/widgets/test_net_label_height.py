"""Net labels default to a PITCH height constraint on the handle rectangle."""

import logging

import pytest
from PyQt6.QtCore    import QObject, QPointF, pyqtSignal
from PyQt6.QtWidgets import QApplication

from ConnectEd.app import ConnectEdApp
from ConnectEd.core.defs import PITCH
from ConnectEd.core.types import AlignV
from ConnectEd.widgets.graphics.items.net_label import NetLabelItem


@pytest.fixture
def connect_ed_app() -> ConnectEdApp:
    app = QApplication.instance()
    if not isinstance(app, ConnectEdApp):
        app = ConnectEdApp()
    assert isinstance(app, ConnectEdApp)

    class _FakeSettings(QObject):
        changed = pyqtSignal(str)

        def get(self, path : str, default=None):
            if path == "defaults/extents":
                return QPointF(1000.0, 1000.0)
            return default

    app.setSettings(_FakeSettings())
    app.setLogger(logging.getLogger("test"))
    return app


def test_net_label_default_height_constraint(connect_ed_app : ConnectEdApp) -> None:
    label = NetLabelItem(name="Name", value="clk")

    assert label.height() == PITCH
    assert label.properties.default("Height") == float(PITCH)
    assert label.handleRect().height() == pytest.approx(PITCH)
    assert label.alignV() == AlignV.MIDDLE
    assert label.properties.default("AlignV") == AlignV.MIDDLE
