"""Port name property text must grow away from the cleat when rotated 180°."""

import logging

import pytest
from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QApplication

from ConnectEd.app import ConnectEdApp
from ConnectEd.core.db import DesignDbNode
from ConnectEd.core.settings import Settings
from ConnectEd.core.types import RectHandleId
from ConnectEd.widgets.graphics.items.block import BlockItem
from ConnectEd.widgets.graphics.items.block_pin import BlockPinItem
from ConnectEd.widgets.graphics.items.port import PortItem
from ConnectEd.widgets.graphics.items.property_text import PropertyTextItem
from ConnectEd.widgets.graphics.scenes.diagram import DiagramScene


@pytest.fixture
def connect_ed_app() -> ConnectEdApp:
    app = QApplication.instance()
    if not isinstance(app, ConnectEdApp):
        app = ConnectEdApp()
    app.setSettings(Settings())
    app.setLogger(logging.getLogger("test"))
    return app


def _text_anchored_to_cleat(pt : PropertyTextItem) -> bool:
    origin = pt.mapToScene(pt.getOriginHandle().pos()).x()
    right_h = pt.mapToScene(pt.getHandle(RectHandleId.MIDDLE_RIGHT).pos()).x()
    rect = pt._child.mapToScene(pt._child.boundingRect()).boundingRect()
    if pt.sceneRotation() > 90:
        return abs(rect.right() - origin) < 1 and abs(rect.left() - right_h) < 1
    return abs(rect.left() - origin) < 1 and abs(rect.right() - right_h) < 1


def _child_scene_rect(port : PortItem) -> tuple[float, float]:
    pt = port.properties.text("Name")
    assert pt is not None
    rect = pt._child.mapToScene(pt._child.boundingRect()).boundingRect()
    return rect.left(), rect.right()


def test_input_port_name_grows_away_from_cleat(
    connect_ed_app : ConnectEdApp,
) -> None:
    scene = DiagramScene()
    port = PortItem()
    port.setRotation(180)
    port.setPos(QPointF(100, 100))
    port.setName("A")
    scene.addItem(port)

    pt = port.properties.text("Name")
    assert pt is not None
    origin_x = pt.mapToScene(pt.getOriginHandle().pos()).x()
    right_h_x = pt.mapToScene(
        pt.getHandle(RectHandleId.MIDDLE_RIGHT).pos()
    ).x()
    child_l, child_r = _child_scene_rect(port)

    port.setName("ABCDEFGH")

    origin_x2 = pt.mapToScene(pt.getOriginHandle().pos()).x()
    right_h_x2 = pt.mapToScene(
        pt.getHandle(RectHandleId.MIDDLE_RIGHT).pos()
    ).x()
    child_l2, child_r2 = _child_scene_rect(port)

    assert origin_x2 == pytest.approx(origin_x)
    assert child_r2 == pytest.approx(origin_x2, abs=0.5)
    assert right_h_x2 == pytest.approx(child_l2, abs=0.5)
    assert right_h_x2 < right_h_x


def test_output_port_name_grows_away_from_cleat(
    connect_ed_app : ConnectEdApp,
) -> None:
    scene = DiagramScene()
    port = PortItem()
    port.setRotation(0)
    port.setPos(QPointF(100, 100))
    port.setName("A")
    scene.addItem(port)

    pt = port.properties.text("Name")
    assert pt is not None
    origin_x = pt.mapToScene(pt.getOriginHandle().pos()).x()
    right_h_x = pt.mapToScene(
        pt.getHandle(RectHandleId.MIDDLE_RIGHT).pos()
    ).x()
    child_l, child_r = _child_scene_rect(port)

    port.setName("ABCDEFGH")

    origin_x2 = pt.mapToScene(pt.getOriginHandle().pos()).x()
    right_h_x2 = pt.mapToScene(
        pt.getHandle(RectHandleId.MIDDLE_RIGHT).pos()
    ).x()
    child_l2, child_r2 = _child_scene_rect(port)

    assert origin_x2 == pytest.approx(origin_x)
    assert child_l2 == pytest.approx(origin_x2, abs=0.5)
    assert right_h_x2 == pytest.approx(child_r2, abs=0.5)
    assert right_h_x2 > right_h_x


def test_loaded_test_dsn_port_and_right_block_pins(
    connect_ed_app : ConnectEdApp,
) -> None:
    db = DesignDbNode.load("examples/test.dsn")
    scene = db.scene()

    port = next(item for item in scene.items() if isinstance(item, PortItem))
    pt = port.properties.text("Name")
    assert pt is not None
    assert _text_anchored_to_cleat(pt)
    pt.onSceneRotationChanged()
    assert _text_anchored_to_cleat(pt)

    block = next(item for item in scene.items() if isinstance(item, BlockItem))
    for pin in block.childItems():
        if not isinstance(pin, BlockPinItem):
            continue
        if pin.loc().edge.value != "Right":
            continue
        pin_pt = pin.properties.text("Name")
        assert pin_pt is not None
        assert _text_anchored_to_cleat(pin_pt)
        pin_pt.onSceneRotationChanged()
        assert _text_anchored_to_cleat(pin_pt)
