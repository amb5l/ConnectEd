"""connectFixedNode and detachFixedNode diagram connectivity."""

import pytest
from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QApplication

from ConnectEd.app import ConnectEdApp
from ConnectEd.core.settings import Settings
from ConnectEd.widgets.graphics.items.node import FreeNodeItem
from ConnectEd.widgets.graphics.items.port import PortItem
from ConnectEd.widgets.graphics.items.segment import SegmentItem
from ConnectEd.widgets.graphics.scenes.diagram import DiagramScene


@pytest.fixture
def connect_ed_app() -> ConnectEdApp:
    app = QApplication.instance()
    if not isinstance(app, ConnectEdApp):
        app = ConnectEdApp()
    app.setSettings(Settings())
    return app


def _wire(
    scene : DiagramScene,
    n1    : FreeNodeItem,
    n2    : FreeNodeItem,
) -> SegmentItem:
    seg = SegmentItem(n1, n2)
    scene.addItem(seg)
    scene.netlist.addSegment(seg)
    return seg


def test_connect_fixed_node_skips_connected(
    connect_ed_app : ConnectEdApp,
) -> None:
    scene = DiagramScene()
    port = PortItem()
    scene.addItem(port)
    port.setPos(0, 0)
    pin = port.node()
    far = FreeNodeItem(QPointF(100, 0))
    scene.addItem(far)
    _wire(scene, pin, far)

    assert pin.degree() == 1
    scene.connectFixedNode(pin)
    assert pin.degree() == 1
    assert scene.netlist.hasSegment(pin, far)


def test_connect_fixed_node_merges_free_node(
    connect_ed_app : ConnectEdApp,
) -> None:
    scene = DiagramScene()
    port = PortItem()
    scene.addItem(port)
    port.setPos(100, 0)
    pin = port.node()

    free = FreeNodeItem(QPointF(100, 0))
    far  = FreeNodeItem(QPointF(200, 0))
    scene.addItem(free)
    scene.addItem(far)
    _wire(scene, free, far)

    assert pin.degree() == 0
    scene.connectFixedNode(pin)

    assert pin.degree() == 1
    assert scene.netlist.hasSegment(pin, far)
    assert free.scene() is None


def test_connect_fixed_node_splits_crossing_segment(
    connect_ed_app : ConnectEdApp,
) -> None:
    scene = DiagramScene()
    n1 = FreeNodeItem(QPointF(0, 0))
    n2 = FreeNodeItem(QPointF(200, 0))
    scene.addItem(n1)
    scene.addItem(n2)
    seg = _wire(scene, n1, n2)

    port = PortItem()
    scene.addItem(port)
    port.setPos(100, 0)
    pin = port.node()
    assert pin.degree() == 0

    scene.connectFixedNode(pin)

    assert pin.degree() == 2
    assert not scene.netlist.hasSegment(n1, n2)
    assert scene.netlist.hasSegment(n1, pin)
    assert scene.netlist.hasSegment(pin, n2)
    assert seg.node1() in (n1, pin) or seg.node2() in (n1, pin)


def test_connect_fixed_node_merge_undo_restores_free_node(
    connect_ed_app : ConnectEdApp,
) -> None:
    scene = DiagramScene()
    port = PortItem()
    scene.addItem(port)
    port.setPos(100, 0)
    pin = port.node()

    free = FreeNodeItem(QPointF(100, 0))
    far  = FreeNodeItem(QPointF(200, 0))
    scene.addItem(free)
    scene.addItem(far)
    _wire(scene, free, far)

    scene.undo_stack.beginMacro("connect")
    scene.connectFixedNode(pin, undoable=True)
    scene.undo_stack.endMacro()

    assert free.scene() is None
    assert scene.netlist.hasSegment(pin, far)

    scene.undo_stack.undo()
    assert free.scene() is not None
    assert scene.netlist.hasSegment(free, far)
    assert pin.degree() == 0


def test_detach_fixed_node_leaves_pin_unconnected(
    connect_ed_app : ConnectEdApp,
) -> None:
    scene = DiagramScene()
    port = PortItem()
    scene.addItem(port)
    port.setPos(0, 0)
    pin = port.node()
    far = FreeNodeItem(QPointF(100, 0))
    scene.addItem(far)
    seg = _wire(scene, pin, far)

    scene.detachFixedNode(pin)

    assert pin.degree() == 0
    assert seg.node1() is not pin and seg.node2() is not pin
    assert seg.node1().degree() == 1 or seg.node2().degree() == 1
