"""ItemSubscribeMixin event registry."""

import pytest
from PyQt6.QtCore    import QObject, QPointF, pyqtSignal
from PyQt6.QtWidgets import QApplication

from ConnectEd.app import ConnectEdApp
from ConnectEd.widgets.graphics.items.mixin.subscribe import ItemSubscribeMixin
from ConnectEd.widgets.graphics.items.node            import FreeNodeItem, SCENE_POS_CHANGE
from ConnectEd.widgets.graphics.items.segment         import SegmentItem


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


class _Host(ItemSubscribeMixin):
    def __init__(self) -> None:
        self.initSubscribe()


class _Recorder:
    def __init__(self) -> None:
        self.count = 0

    def onGeometryChanged(self) -> None:
        self.count += 1

    def onCustom(self) -> None:
        self.count += 10


def test_subscribe_emit_calls_method() -> None:
    host = _Host()
    rec  = _Recorder()
    host.subscribe(SCENE_POS_CHANGE, rec, "onGeometryChanged")
    host.callSubscribers(SCENE_POS_CHANGE)
    assert rec.count == 1


def test_unsubscribe_stops_notifications() -> None:
    host = _Host()
    rec  = _Recorder()
    host.subscribe(SCENE_POS_CHANGE, rec, "onGeometryChanged")
    host.unsubscribe(SCENE_POS_CHANGE, rec)
    host.callSubscribers(SCENE_POS_CHANGE)
    assert rec.count == 0


def test_custom_method_name() -> None:
    host = _Host()
    rec  = _Recorder()
    host.subscribe(SCENE_POS_CHANGE, rec, "onCustom")
    host.callSubscribers(SCENE_POS_CHANGE)
    assert rec.count == 10


def test_events_are_independent() -> None:
    host = _Host()
    rec  = _Recorder()
    host.subscribe(SCENE_POS_CHANGE, rec, "onGeometryChanged")
    host.callSubscribers("other")
    assert rec.count == 0


def test_subscribe_overwrites_method_for_same_dependent() -> None:
    host = _Host()
    rec  = _Recorder()
    host.subscribe(SCENE_POS_CHANGE, rec, "onGeometryChanged")
    host.subscribe(SCENE_POS_CHANGE, rec, "onCustom")
    host.callSubscribers(SCENE_POS_CHANGE)
    assert rec.count == 10


def test_segment_subscribes_to_endpoint_nodes(connect_ed_app : ConnectEdApp) -> None:
    n1  = FreeNodeItem(QPointF(0, 0))
    n2  = FreeNodeItem(QPointF(100, 0))
    seg = SegmentItem(n1, n2)
    assert seg in n1._subs[SCENE_POS_CHANGE]
    assert seg in n2._subs[SCENE_POS_CHANGE]
    assert n1._subs[SCENE_POS_CHANGE][seg] == SegmentItem._SCENE_POS_METHOD


def test_segment_unsubscribes_on_disconnect(connect_ed_app : ConnectEdApp) -> None:
    n1  = FreeNodeItem(QPointF(0, 0))
    n2  = FreeNodeItem(QPointF(100, 0))
    seg = SegmentItem(n1, n2)
    seg.setNode1(None)
    assert seg not in n1._subs[SCENE_POS_CHANGE]
    assert seg in n2._subs[SCENE_POS_CHANGE]


def test_node_scene_pos_change_updates_segment(connect_ed_app : ConnectEdApp) -> None:
    n1  = FreeNodeItem(QPointF(0, 0))
    n2  = FreeNodeItem(QPointF(100, 0))
    seg = SegmentItem(n1, n2)
    n1.setPos(20, 0)
    n1.onScenePositionChanged(n1.scenePos())
    assert seg.scenePos().x() == pytest.approx(20.0)
