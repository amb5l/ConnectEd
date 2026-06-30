"""PropertyLayout must resolve owner properties (e.g. Block Label), not PropertyText names."""

import pytest
from PyQt6.QtCore    import QObject, QPointF, pyqtSignal
from PyQt6.QtWidgets import QApplication, QLabel

from ConnectEd.app import ConnectEdApp
from ConnectEd.widgets.dialogs.components.edit import StrEditor
from ConnectEd.widgets.dialogs.components.layout.property import PropertyLayout
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


def test_property_layout_resolves_block_label(connect_ed_app : ConnectEdApp) -> None:
    block = BlockItem(QPointF(0.0, 0.0), QPointF(100.0, 50.0))
    block.setLabel("U1")
    label_pt = block.properties.text("Label")
    assert label_pt is not None

    layout = PropertyLayout(label_pt, "Label")

    assert layout._owner_value.text() != PropertyLayout._NOT_FOUND
    assert isinstance(layout._kind_value, QLabel)
    assert layout._kind_value.text() == "String"
    assert isinstance(layout._value_value, StrEditor)
    assert layout._value_value.text() == "U1"
