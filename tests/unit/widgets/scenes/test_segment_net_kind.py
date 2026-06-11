"""Segment appearance driven by NetKind from netlist resolution."""

import pytest
from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QApplication

from ConnectEd.app import ConnectEdApp
from ConnectEd.core.settings import Settings
from ConnectEd.core.types import NetKind
from ConnectEd.widgets.graphics.items.node import FreeNodeItem
from ConnectEd.widgets.graphics.items.segment import SegmentItem
from ConnectEd.widgets.graphics.scenes.diagram import DiagramScene
from ConnectEd.widgets.graphics.scenes.diagram.netlist import _netKindFromSuffix
from ConnectEd.widgets.graphics.scenes.diagram.resources import DiagramSceneResources


@pytest.fixture
def connect_ed_app() -> ConnectEdApp:
    app = QApplication.instance()
    if not isinstance(app, ConnectEdApp):
        app = ConnectEdApp()
    app.setSettings(Settings())
    return app


def test_net_kind_from_suffix() -> None:
    assert _netKindFromSuffix(None) == NetKind.UNRESOLVED
    assert _netKindFromSuffix("") == NetKind.SCALAR
    assert _netKindFromSuffix("3") == NetKind.SCALAR
    assert _netKindFromSuffix("31:0") == NetKind.VECTOR


def test_segment_resources_net_kind_pens(
    connect_ed_app : ConnectEdApp,
) -> None:
    resources = DiagramSceneResources()
    scalar = resources.pen("Segment", (NetKind.SCALAR, False))
    vector = resources.pen("Segment", (NetKind.VECTOR, False))
    assert scalar.widthF() == 1.0
    assert vector.widthF() == 2.0


def test_segment_net_kind_updates_on_resolve(
    connect_ed_app : ConnectEdApp,
) -> None:
    scene = DiagramScene()
    n1 = FreeNodeItem(QPointF(0, 0))
    n2 = FreeNodeItem(QPointF(100, 0))
    scene.addItem(n1)
    scene.addItem(n2)
    seg = SegmentItem(n1, n2)
    scene.addItem(seg)
    scene.netlist.addSegment(seg)

    assert seg.netKind() == NetKind.UNRESOLVED

    subnet = scene.netlist.nodeSubnet(n1)
    assert subnet is not None
    subnet.name = "DATA"
    subnet.suffix = "31:0"
    scene.netlist._refreshSegments([subnet])

    assert seg.netKind() == NetKind.VECTOR
    assert seg.pen().widthF() == 2.0


def test_add_segment_refreshes_net_kind_after_resolve(
    connect_ed_app : ConnectEdApp,
) -> None:
    scene = DiagramScene()
    n1 = FreeNodeItem(QPointF(0, 0))
    n2 = FreeNodeItem(QPointF(100, 0))
    scene.addItem(n1)
    scene.addItem(n2)
    seg = SegmentItem(n1, n2)
    scene.addItem(seg)
    assert seg.netKind() == NetKind.UNRESOLVED

    netlist = scene.netlist
    original_resolve = netlist._resolveSubnet

    def resolve_and_name(subnet : object, trail : list[int] | None = None) -> None:
        original_resolve(subnet, trail)
        subnet.name   = "X"  # type: ignore[attr-defined]
        subnet.suffix = "7:0"  # type: ignore[attr-defined]

    netlist._resolveSubnet = resolve_and_name
    netlist.addSegment(seg)

    assert seg.netKind() == NetKind.VECTOR
    assert seg.pen().widthF() == 2.0


def test_two_segments_same_subnet_both_vector(
    connect_ed_app : ConnectEdApp,
) -> None:
    scene = DiagramScene()
    port = FreeNodeItem(QPointF(0, 0))
    corner = FreeNodeItem(QPointF(100, 0))
    end = FreeNodeItem(QPointF(100, 100))
    for node in (port, corner, end):
        scene.addItem(node)
    seg1 = SegmentItem(port, corner)
    seg2 = SegmentItem(corner, end)
    scene.addItem(seg1)
    scene.addItem(seg2)

    netlist = scene.netlist
    original_resolve = netlist._resolveSubnet

    def resolve_and_name(subnet : object, trail : list[int] | None = None) -> None:
        original_resolve(subnet, trail)
        subnet.name   = "X"  # type: ignore[attr-defined]
        subnet.suffix = "7:0"  # type: ignore[attr-defined]

    netlist._resolveSubnet = resolve_and_name
    netlist.addSegment(seg1)
    netlist.addSegment(seg2)

    assert seg1.netKind() == NetKind.VECTOR
    assert seg2.netKind() == NetKind.VECTOR
    assert seg1.pen().widthF() == 2.0
    assert seg2.pen().widthF() == 2.0


def test_net_kind_for_segment_prefers_net_suffix(
    connect_ed_app : ConnectEdApp,
) -> None:
    scene = DiagramScene()
    n1 = FreeNodeItem(QPointF(0, 0))
    n2 = FreeNodeItem(QPointF(0, 100))
    scene.addItem(n1)
    scene.addItem(n2)
    seg = SegmentItem(n1, n2)
    scene.addItem(seg)
    scene.netlist.addSegment(seg)

    subnet = scene.netlist.nodeSubnet(n1)
    assert subnet is not None
    subnet.name = "DATA"
    subnet.suffix = "3"
    net = subnet.net
    assert net is not None
    net.suffix = "31:0"
    scene.netlist._refreshSegments([subnet])

    assert scene.netlist.netKindForSegment(seg) == NetKind.VECTOR
    assert seg.netKind() == NetKind.VECTOR
