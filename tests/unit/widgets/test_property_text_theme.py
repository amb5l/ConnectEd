"""PropertyTextItem must resolve themed quills (e.g. BlockName → mid_cyan)."""

import pytest
from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QApplication

from ConnectEd.app import ConnectEdApp
from ConnectEd.core.settings import Settings
from ConnectEd.core.palette import mid_cyan, mid_red
from ConnectEd.widgets.graphics.items.block import BlockItem
from ConnectEd.widgets.graphics.items.property_text import PropertyTextItem
from ConnectEd.widgets.graphics.scenes.drawing.resources import DrawingSceneResources


@pytest.fixture
def connect_ed_app() -> ConnectEdApp:
    app = QApplication.instance()
    if not isinstance(app, ConnectEdApp):
        app = ConnectEdApp()
    app.setSettings(Settings())
    return app


def test_property_text_block_name_settings_and_resources(
    connect_ed_app : ConnectEdApp,
) -> None:
    block = BlockItem(QPointF(0.0, 0.0), QPointF(100.0, 50.0))
    pt = block.properties.text("Name")
    assert pt is not None
    assert pt.settingsName() == "BlockName"
    assert pt.resourcesName() == "BlockName"


def test_property_text_unknown_property_falls_back(
    connect_ed_app : ConnectEdApp,
) -> None:
    block = BlockItem(QPointF(0.0, 0.0), QPointF(100.0, 50.0))
    pt = PropertyTextItem(name="", parent=block)
    pt._name = "CustomProp"
    assert pt.settingsName() == "PropertyText"
    assert pt.resourcesName() == "PropertyText"


def test_resources_quill_lazy_loads_block_name_color(
    connect_ed_app : ConnectEdApp,
) -> None:
    resources = DrawingSceneResources()
    quill = resources.quill("BlockName", False)
    assert quill.color() == mid_cyan
    assert quill.color() != mid_red


def test_resources_quill_lazy_loads_property_text_fallback(
    connect_ed_app : ConnectEdApp,
) -> None:
    resources = DrawingSceneResources()
    quill = resources.quill("PropertyText", False)
    assert quill.color() == mid_red
