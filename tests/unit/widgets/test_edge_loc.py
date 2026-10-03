"""Resize keeps an edge-located pin on its edge and inside both corners."""

from __future__ import annotations

import pytest

from typing import TypeVar, cast

from PyQt6.QtCore    import QObject, QPointF, QRectF, pyqtSignal
from PyQt6.QtWidgets import QApplication, QGraphicsItem

from ConnectEd.app           import ConnectEdApp
from ConnectEd.core.defs     import PITCH
from ConnectEd.core.settings import Settings
from ConnectEd.core.types    import Edge, EdgeLoc, RectHandleId

from ConnectEd.widgets.graphics.items.block      import BlockItem
from ConnectEd.widgets.graphics.items.block_pin  import BlockPinItem
from ConnectEd.widgets.graphics.items.symbol     import SymbolDefinitionItem
from ConnectEd.widgets.graphics.items.symbol_pin import SymbolPinItem

PinT = TypeVar("PinT", BlockPinItem, SymbolPinItem)


_LEFT = frozenset({
    RectHandleId.TOP_LEFT,
    RectHandleId.MIDDLE_LEFT,
    RectHandleId.BOTTOM_LEFT,
})
_RIGHT = frozenset({
    RectHandleId.TOP_RIGHT,
    RectHandleId.MIDDLE_RIGHT,
    RectHandleId.BOTTOM_RIGHT,
})
_TOP = frozenset({
    RectHandleId.TOP_LEFT,
    RectHandleId.TOP_CENTER,
    RectHandleId.TOP_RIGHT,
})
_BOTTOM = frozenset({
    RectHandleId.BOTTOM_LEFT,
    RectHandleId.BOTTOM_CENTER,
    RectHandleId.BOTTOM_RIGHT,
})
_RESIZE = (
    RectHandleId.TOP_LEFT,
    RectHandleId.TOP_CENTER,
    RectHandleId.TOP_RIGHT,
    RectHandleId.MIDDLE_LEFT,
    RectHandleId.MIDDLE_RIGHT,
    RectHandleId.BOTTOM_LEFT,
    RectHandleId.BOTTOM_CENTER,
    RectHandleId.BOTTOM_RIGHT,
)
_PIN_AT = (
    (Edge.LEFT  , 20.0),
    (Edge.RIGHT , 40.0),
    (Edge.TOP   , 30.0),
    (Edge.BOTTOM, 50.0),
)


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

    app.setSettings(cast(Settings, _FakeSettings()))
    return app


def _close(a : QPointF, b : QPointF) -> None:
    assert a.x() == pytest.approx(b.x())
    assert a.y() == pytest.approx(b.y())


def _anchor(body : QGraphicsItem, pin : QGraphicsItem) -> QPointF:
    return body.mapToParent(QGraphicsItem.pos(pin))


def _length(body : BlockItem | SymbolDefinitionItem, edge : Edge) -> float:
    if edge in (Edge.LEFT, Edge.RIGHT):
        return body.height()
    return body.width()


def _offsets(
    pins  : list[PinT],
    edges : tuple[Edge, ...]
) -> list[float]:
    found : list[float] = []
    for pin in pins:
        loc = pin.loc()
        if loc.edge in edges and loc.offset is not None:
            found.append(loc.offset)
    return found


def _place(
    body : BlockItem | SymbolDefinitionItem,
    kind : type[PinT]
) -> list[PinT]:
    pins : list[PinT] = []
    for edge, offset in _PIN_AT:
        pin = kind()
        pin.setParentItem(body)
        pin.setLoc(EdgeLoc(edge, offset))
        pins.append(pin)
    return pins


def _outward(handle : RectHandleId) -> QPointF:
    span = float(2 * PITCH)
    dx = -span if handle in _LEFT else span if handle in _RIGHT else 0.0
    dy = -span if handle in _TOP else span if handle in _BOTTOM else 0.0
    return QPointF(dx, dy)


def _inward(
    body   : BlockItem | SymbolDefinitionItem,
    pins   : list[PinT],
    handle : RectHandleId
) -> QPointF:
    extra = float(PITCH) + 5.0
    dx    = 0.0
    dy    = 0.0
    if handle in _LEFT:
        dx = min(_offsets(pins, (Edge.TOP, Edge.BOTTOM))) + extra
    elif handle in _RIGHT:
        gap = body.width() - max(_offsets(pins, (Edge.TOP, Edge.BOTTOM)))
        dx  = -(gap + extra)
    if handle in _TOP:
        dy = min(_offsets(pins, (Edge.LEFT, Edge.RIGHT))) + extra
    elif handle in _BOTTOM:
        gap = body.height() - max(_offsets(pins, (Edge.LEFT, Edge.RIGHT)))
        dy  = -(gap + extra)
    return QPointF(dx, dy)


def _moved(handle : RectHandleId) -> set[Edge]:
    edges : set[Edge] = set()
    if handle in _LEFT:
        edges.add(Edge.LEFT)
    if handle in _RIGHT:
        edges.add(Edge.RIGHT)
    if handle in _TOP:
        edges.add(Edge.TOP)
    if handle in _BOTTOM:
        edges.add(Edge.BOTTOM)
    return edges


def _assert_pins(
    body    : BlockItem | SymbolDefinitionItem,
    pins    : list[PinT],
    edges   : dict[PinT, Edge],
    anchors : dict[PinT, QPointF],
    moved   : set[Edge]
) -> None:
    for pin in pins:
        loc = pin.loc()
        assert loc.edge is edges[pin]
        assert loc.edge is not None and loc.offset is not None
        assert loc.offset >= -1e-9
        assert loc.offset <= _length(body, loc.edge) + 1e-9
        _close(QGraphicsItem.pos(pin), body.loc2pos(loc))
        now = _anchor(body, pin)
        old = anchors[pin]
        if loc.edge in (Edge.LEFT, Edge.RIGHT):
            assert now.y() == pytest.approx(old.y())
        else:
            assert now.x() == pytest.approx(old.x())
        if loc.edge in moved:
            if loc.edge in (Edge.LEFT, Edge.RIGHT):
                assert now.x() != pytest.approx(old.x())
            else:
                assert now.y() != pytest.approx(old.y())
        else:
            _close(now, old)


def _assert_stopped(
    body   : BlockItem | SymbolDefinitionItem,
    pins   : list[PinT],
    handle : RectHandleId,
    before : dict[PinT, float]
) -> None:
    if handle in _LEFT:
        limit = min(
            before[pin] for pin in pins if pin.loc().edge in (Edge.TOP, Edge.BOTTOM)
        )
        for pin in pins:
            if pin.loc().edge in (Edge.TOP, Edge.BOTTOM) \
            and before[pin] == pytest.approx(limit):
                assert pin.loc().offset == pytest.approx(0.0)
    if handle in _RIGHT:
        assert body.width() == pytest.approx(max(
            float(PITCH),
            max(pin.loc().offset or 0.0 for pin in pins
                if pin.loc().edge in (Edge.TOP, Edge.BOTTOM))
        ))
    if handle in _TOP:
        limit = min(
            before[pin] for pin in pins if pin.loc().edge in (Edge.LEFT, Edge.RIGHT)
        )
        for pin in pins:
            if pin.loc().edge in (Edge.LEFT, Edge.RIGHT) \
            and before[pin] == pytest.approx(limit):
                assert pin.loc().offset == pytest.approx(0.0)
    if handle in _BOTTOM:
        assert body.height() == pytest.approx(max(
            float(PITCH),
            max(pin.loc().offset or 0.0 for pin in pins
                if pin.loc().edge in (Edge.LEFT, Edge.RIGHT))
        ))


def _exercise(
    body : BlockItem | SymbolDefinitionItem,
    kind : type[PinT]
) -> None:
    pins = _place(body, kind)
    edges : dict[PinT, Edge] = {}
    for pin in pins:
        edge = pin.loc().edge
        assert edge is not None
        edges[pin] = edge
    for handle in _RESIZE:
        anchors = {pin: _anchor(body, pin) for pin in pins}
        width   = body.width()
        height  = body.height()
        delta   = _outward(handle)
        body.moveHandleBy(handle, delta)
        assert body.width()  == pytest.approx(width  + abs(delta.x()))
        assert body.height() == pytest.approx(height + abs(delta.y()))
        _assert_pins(body, pins, edges, anchors, _moved(handle))

        anchors = {pin: _anchor(body, pin) for pin in pins}
        before  = {pin: pin.loc().offset or 0.0 for pin in pins}
        body.moveHandleBy(handle, _inward(body, pins, handle))
        _assert_pins(body, pins, edges, anchors, _moved(handle))
        _assert_stopped(body, pins, handle, before)


def test_block_resize_keeps_pins_on_edges(connect_ed_app : ConnectEdApp) -> None:
    del connect_ed_app
    block = BlockItem(QPointF(100.0, 40.0), QPointF(180.0, 100.0))
    _exercise(block, BlockPinItem)


def test_symbol_resize_keeps_pins_on_edges(connect_ed_app : ConnectEdApp) -> None:
    del connect_ed_app
    body = SymbolDefinitionItem()
    body.setPos(QPointF(100.0, 40.0))
    body.setRect(QRectF(0.0, 0.0, 80.0, 60.0))
    _exercise(body, SymbolPinItem)
