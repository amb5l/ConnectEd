"""PropertyLayout must resolve owner properties (e.g. Block Label), not Label names."""

import pytest

from PyQt6.QtCore    import QObject, QPointF, pyqtSignal
from PyQt6.QtWidgets import QApplication, QLabel

from ConnectEd.app import ConnectEdApp

from ConnectEd.widgets.dialogs.components.edit import StrEditor

from ConnectEd.widgets.dialogs.items.label import PropertyLayout

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
    block.setReference("U1")
    labels = block.labelItems(block.properties["Reference"])
    assert labels
    label = labels[0]
    assert label.name() == "Reference"

    layout = PropertyLayout(label, "Reference")

    assert isinstance(layout._name_value, QLabel)
    assert layout._name_value.text() == "Reference"
    assert isinstance(layout._kind_value, QLabel)
    assert layout._kind_value.text() == "String"
    assert isinstance(layout._value_value, StrEditor)
    assert layout._value_value.text() == "U1"
