"""LabelItem must resolve themed quills (e.g. BlockName → sky blue)."""

import pytest

from PyQt6.QtCore    import QPointF
from PyQt6.QtGui     import QColor
from PyQt6.QtWidgets import QApplication

from ConnectEd.app import ConnectEdApp

from ConnectEd.core.palette  import bright_magenta
from ConnectEd.core.settings import Settings
from ConnectEd.core.types    import DataKind

from ConnectEd.widgets.graphics.items.block              import BlockItem
from ConnectEd.widgets.graphics.items.block_pin          import BlockPinItem
from ConnectEd.widgets.graphics.items.label              import LabelItem
from ConnectEd.widgets.graphics.scenes.diagram           import DiagramScene

from ConnectEd.widgets.graphics.scenes.diagram.resources import DiagramSceneResources


@pytest.fixture
def connect_ed_app() -> ConnectEdApp:
    app = QApplication.instance()
    if not isinstance(app, ConnectEdApp):
        app = ConnectEdApp()
    app.setSettings(Settings())
    return app


def test_label_block_name_settings_and_resources(
    connect_ed_app : ConnectEdApp,
) -> None:
    block = BlockItem(QPointF(0.0, 0.0), QPointF(100.0, 50.0))
    labels = block.labelItems(block.properties["Name"])
    assert labels
    label = labels[0]
    assert label.name() == "Name"
    assert label.settingsName() == "BlockName"
    assert label.resourcesName() == "BlockName"


def test_label_unknown_property_falls_back(
    connect_ed_app : ConnectEdApp,
) -> None:
    block = BlockItem(QPointF(0.0, 0.0), QPointF(100.0, 50.0))
    prop = block.propertyAdd("CustomProp", DataKind.STR, "x")
    assert prop is not None
    label = LabelItem(property=prop)
    assert label.name() == "CustomProp"
    assert label.settingsName() == "Label"
    assert label.resourcesName() == "Label"


def test_resources_quill_lazy_loads_block_name_color(
    connect_ed_app : ConnectEdApp,
) -> None:
    resources = DiagramSceneResources()
    quill = resources.quill("BlockName", False)
    assert quill.color() == QColor("#85C2FF")
    assert quill.color() != QColor("#E394DC")


def test_resources_quill_lazy_loads_label_fallback(
    connect_ed_app : ConnectEdApp,
) -> None:
    resources = DiagramSceneResources()
    quill = resources.quill("Label", False)
    assert quill.color() == QColor("#E394DC")


def test_block_pin_name_turns_magenta_when_selected(
    connect_ed_app : ConnectEdApp,
) -> None:
    scene = DiagramScene()
    pin = BlockPinItem()
    pin.setName("clk")
    scene.addItem(pin)
    labels = pin.labelItems(pin.properties["Name"])
    assert labels
    label = labels[0]
    assert label.color() != bright_magenta
    label.setSelected(True)
    assert label.color() == bright_magenta
    label.setSelected(False)
    assert label.color() != bright_magenta
